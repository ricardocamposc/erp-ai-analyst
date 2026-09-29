"""LangGraph coordinator for dynamic agentic query execution."""

from datetime import date
from typing import Any, TypedDict, cast

from langgraph.graph import END, START, StateGraph

from app.agent.contracts import FinalAnswer
from app.query.agents import DynamicAgentGateway
from app.query.audit import fail_interaction, record_interaction, update_interaction
from app.query.contracts import (
    QueryMetadata,
    QueryProposal,
    QueryResult,
    ValidationResult,
    ValidatorReview,
)
from app.query.guardrails import validate_query
from app.query.provider import LocalERPQueryProvider
from app.query.tools import execute_readonly_query


class DynamicAnalysisState(TypedDict, total=False):
    request_id: str
    question: str
    metadata: QueryMetadata
    proposal: QueryProposal
    validation: ValidationResult
    review: ValidatorReview
    result: QueryResult
    answer: FinalAnswer
    feedback: list[str]
    revision_count: int
    route: str
    execution_error: str


def _temporal_context(state: DynamicAnalysisState) -> dict[str, Any]:
    """Return runtime-derived period labels for synthesis and audit evidence."""

    proposal = state.get("proposal")
    metadata = state.get("metadata")
    if (
        proposal is None
        or metadata is None
        or proposal.temporal_scope != "system_relative"
    ):
        return {}
    system_date = metadata.system_date
    if system_date is None:
        return {}
    current_start = system_date.replace(day=1)
    previous_end = current_start.fromordinal(current_start.toordinal() - 1)
    previous_start = previous_end.replace(day=1)
    return {
        "scope": "system_relative",
        "system_date": system_date.isoformat(),
        "current_period_start": current_start.isoformat(),
        "current_period_label": current_start.strftime("%Y-%m"),
        "previous_period_start": previous_start.isoformat(),
        "previous_period_end": previous_end.isoformat(),
        "previous_period_label": previous_start.strftime("%Y-%m"),
        "source": "runtime system date; not inferred from the answer",
    }


def _result_grain_issue(state: DynamicAnalysisState, result: QueryResult) -> str | None:
    """Reject a multi-row result where the requested comparison requires one row."""

    proposal = state.get("proposal")
    if proposal is None or result.row_count <= 1:
        return None
    if (
        proposal.analysis_mode == "comparison"
        and proposal.temporal_scope == "system_relative"
    ):
        return (
            "system-relative period comparison returned more than one row; "
            "aggregate each current and previous period into one row and remove daily or "
            "transaction-level GROUP BY expressions unless the user explicitly requested detail"
        )
    return None


def build_dynamic_graph(
    provider: LocalERPQueryProvider | None = None,
    gateway: DynamicAgentGateway | None = None,
) -> Any:
    active_provider = provider or LocalERPQueryProvider()
    active_gateway = gateway or DynamicAgentGateway()

    def discover(state: DynamicAnalysisState) -> dict[str, Any]:
        update_interaction(
            request_id=state["request_id"], stage="discover", status="running"
        )
        metadata = active_provider.metadata()
        periods: dict[str, dict[str, Any]] = {}
        get_periods = getattr(active_provider, "available_periods", None)
        if get_periods is not None:
            for table in metadata.tables:
                if table.temporal_columns:
                    periods[table.name] = get_periods(table.name)
            metadata = metadata.model_copy(
                update={"available_periods": periods, "system_date": date.today()}
            )
        else:
            metadata = metadata.model_copy(update={"system_date": date.today()})
        update_interaction(
            request_id=state["request_id"],
            stage="discover",
            status="completed",
            response={
                "catalog_version": metadata.catalog_version,
                "available_periods": periods,
            },
        )
        return {"metadata": metadata}

    def route_question(state: DynamicAnalysisState) -> dict[str, Any]:
        update_interaction(
            request_id=state["request_id"], stage="route", status="running"
        )
        route = active_gateway.route_question(state["question"])
        update_interaction(
            request_id=state["request_id"],
            stage="route",
            status="completed",
            response={"route": route.model_dump(mode="json")},
        )
        return {"route": route.kind}

    def analyze(state: DynamicAnalysisState) -> dict[str, Any]:
        update_interaction(
            request_id=state["request_id"], stage="analyze", status="running"
        )
        proposal = active_gateway.analyze(
            state["question"], state["metadata"], state.get("feedback", [])
        )
        update_interaction(
            request_id=state["request_id"],
            stage="analyze",
            status="completed",
            response={"query": proposal.model_dump(mode="json")},
        )
        return {
            "proposal": proposal,
            "revision_count": state.get("revision_count", 0) + 1,
            "execution_error": "",
        }

    def validate(state: DynamicAnalysisState) -> dict[str, Any]:
        update_interaction(
            request_id=state["request_id"], stage="validate", status="running"
        )
        validation = validate_query(state["proposal"], state["metadata"])
        if validation.diagnostic_sql:
            try:
                active_provider.explain_readonly(validation.diagnostic_sql)
            except Exception as error:
                validation = validation.model_copy(
                    update={
                        "status": "rejected"
                        if validation.status == "approved"
                        else validation.status,
                        "normalized_sql": None
                        if validation.status == "approved"
                        else validation.normalized_sql,
                        "reasons": validation.reasons
                        + [f"database validation failed: {error}"],
                    }
                )
        update_interaction(
            request_id=state["request_id"],
            stage="validate",
            status=validation.status,
            response={"validation": validation.model_dump(mode="json")},
        )
        return {"validation": validation}

    def review(state: DynamicAnalysisState) -> dict[str, Any]:
        update_interaction(
            request_id=state["request_id"], stage="review", status="running"
        )
        review_result = active_gateway.review(
            state["proposal"],
            state["validation"],
            state["metadata"],
            state["validation"].status == "approved",
        )
        if state[
            "validation"
        ].status == "approved" and review_result.blocking_scope in {
            "coverage",
            "temporal",
        }:
            review_result = review_result.model_copy(update={"blocking_issue": False})
        if state["validation"].status == "approved" and not review_result.approved:
            # The database has already accepted the read-only statement. Before execution,
            # the LLM can only provide an advisory semantic review because it has no result
            # evidence yet. The authoritative semantic gate runs after PostgreSQL returns
            # rows (or an empty result), where the reviewer can compare the answer to facts.
            review_result = review_result.model_copy(update={"blocking_issue": False})
        if (
            state["validation"].status == "approved"
            and not review_result.approved
            and review_result.blocking_issue
        ):
            review_result = active_gateway.adjudicate_review(
                state["proposal"],
                state["validation"],
                review_result,
                state["metadata"],
            )
        update_interaction(
            request_id=state["request_id"],
            stage="review",
            status="completed"
            if review_result.approved or not review_result.blocking_issue
            else "rejected",
            response={"review": review_result.model_dump(mode="json")},
        )
        feedback = (
            state["validation"].reasons
            + review_result.semantic_issues
            + review_result.revision_instructions
        )
        return {"review": review_result, "feedback": feedback}

    def review_result(state: DynamicAnalysisState) -> dict[str, Any]:
        """Review the executed result while preserving the pre-execution gate."""
        update_interaction(
            request_id=state["request_id"], stage="review", status="running"
        )
        review_result = active_gateway.review(
            state["proposal"],
            state["validation"],
            state["metadata"],
            True,
            state["result"].model_dump(mode="json"),
        )
        if not review_result.approved and review_result.blocking_issue:
            review_result = active_gateway.adjudicate_review(
                state["proposal"],
                state["validation"],
                review_result,
                state["metadata"],
                state["result"].model_dump(mode="json"),
            )
        if (
            state["validation"].status == "approved"
            and state["result"].row_count > 0
            and review_result.blocking_scope in {"coverage", "temporal"}
        ):
            # PostgreSQL accepted the read-only query and returned evidence. A semantic
            # objection without a proven entity/metric mismatch remains a warning; it must
            # not discard a valid result after execution.
            review_result = review_result.model_copy(update={"blocking_issue": False})
        update_interaction(
            request_id=state["request_id"],
            stage="review",
            status="completed"
            if review_result.approved or not review_result.blocking_issue
            else "rejected",
            response={"review": review_result.model_dump(mode="json")},
        )
        return {
            "review": review_result,
            "feedback": review_result.semantic_issues
            + review_result.revision_instructions,
        }

    def route(state: DynamicAnalysisState) -> str:
        if state.get("execution_error") and state.get("revision_count", 0) < 3:
            return "analyze"
        if state["validation"].status == "approved" and (
            state["review"].approved or not state["review"].blocking_issue
        ):
            return "execute"
        if state.get("revision_count", 0) < 3:
            return "analyze"
        return "finish"

    def execute(state: DynamicAnalysisState) -> dict[str, Any]:
        update_interaction(
            request_id=state["request_id"], stage="execute", status="running"
        )
        try:
            result = execute_readonly_query(active_provider, state["proposal"], 500)
            grain_issue = _result_grain_issue(state, result)
            if grain_issue:
                update_interaction(
                    request_id=state["request_id"],
                    stage="execute",
                    status="failed",
                    response={"warnings": [grain_issue], "row_count": result.row_count},
                )
                return {"execution_error": grain_issue, "feedback": [grain_issue]}
            result = result.model_copy(
                update={"temporal_context": _temporal_context(state)}
            )
        except Exception as error:
            update_interaction(
                request_id=state["request_id"],
                stage="execute",
                status="failed",
                response={"warnings": [str(error)]},
            )
            return {"execution_error": str(error), "feedback": [str(error)]}
        update_interaction(
            request_id=state["request_id"],
            stage="execute",
            status="completed",
            response={"result": result.model_dump(mode="json")},
        )
        return {"result": result}

    def conceptual_answer(state: DynamicAnalysisState) -> dict[str, Any]:
        update_interaction(
            request_id=state["request_id"], stage="synthesize", status="running"
        )
        answer = active_gateway.answer_concept(state["question"])
        update_interaction(
            request_id=state["request_id"],
            stage="synthesize",
            status=answer.status,
            response=answer.model_dump(mode="json"),
        )
        return {"answer": answer}

    def unsupported_answer(state: DynamicAnalysisState) -> dict[str, Any]:
        update_interaction(
            request_id=state["request_id"], stage="synthesize", status="running"
        )
        answer = active_gateway.answer_unsupported(state["question"])
        update_interaction(
            request_id=state["request_id"],
            stage="synthesize",
            status=answer.status,
            response=answer.model_dump(mode="json"),
        )
        return {"answer": answer}

    def finish(state: DynamicAnalysisState) -> dict[str, Any]:
        review = state.get("review", ValidatorReview(approved=True))
        if "result" not in state or (not review.approved and review.blocking_issue):
            if any(
                "system-relative period" in reason
                for reason in state["validation"].reasons
            ):
                return {
                    "answer": active_gateway.synthesize_no_data(
                        state["question"],
                        str(state["metadata"].system_date),
                        state["metadata"].available_periods,
                    )
                }
            warnings = (
                state["validation"].reasons
                + state["review"].semantic_issues
                + ([state["execution_error"]] if state.get("execution_error") else [])
            )
            return {
                "answer": active_gateway.synthesize_insufficient(
                    state["question"], warnings
                )
            }
        return {
            "answer": active_gateway.synthesize(
                state["question"], state["result"].model_dump(mode="json")
            )
        }

    builder = StateGraph(DynamicAnalysisState)
    builder.add_node("discover", discover)
    builder.add_node("route", route_question)
    builder.add_node("analyze", analyze)
    builder.add_node("validate", validate)
    builder.add_node("review", review)
    builder.add_node("execute", execute)
    builder.add_node("conceptual_answer", conceptual_answer)
    builder.add_node("unsupported_answer", unsupported_answer)
    builder.add_node("finish", finish)
    builder.add_edge(START, "discover")
    builder.add_edge("discover", "route")
    builder.add_conditional_edges(
        "route",
        lambda state: (
            "conceptual_answer"
            if state["route"] == "erp_concept"
            else "unsupported_answer"
            if state["route"] == "unsupported"
            else "analyze"
        ),
        {
            "conceptual_answer": "conceptual_answer",
            "unsupported_answer": "unsupported_answer",
            "analyze": "analyze",
        },
    )
    builder.add_edge("analyze", "validate")
    builder.add_edge("validate", "review")
    builder.add_conditional_edges(
        "review",
        route,
        {"analyze": "analyze", "execute": "execute", "finish": "finish"},
    )
    builder.add_conditional_edges(
        "execute",
        lambda state: (
            "analyze"
            if state.get("execution_error") and state.get("revision_count", 0) < 3
            else "finish"
            if state.get("execution_error")
            else "review_result"
        ),
        {"analyze": "analyze", "review_result": "review_result", "finish": "finish"},
    )
    builder.add_node("review_result", review_result)
    builder.add_conditional_edges(
        "review_result",
        lambda state: (
            "finish"
            if state["review"].approved
            or not state["review"].blocking_issue
            or state.get("revision_count", 0) >= 3
            else "analyze"
        ),
        {"finish": "finish", "analyze": "analyze"},
    )
    builder.add_edge("conceptual_answer", END)
    builder.add_edge("unsupported_answer", END)
    builder.add_edge("finish", END)
    return builder.compile()


def run_dynamic_analysis(
    question: str,
    request_id: str,
    conversation_id: str | None = None,
    provider: LocalERPQueryProvider | None = None,
    gateway: DynamicAgentGateway | None = None,
) -> dict[str, Any]:
    graph = build_dynamic_graph(provider, gateway)
    try:
        state = cast(
            DynamicAnalysisState,
            graph.invoke(
                {"question": question, "request_id": request_id, "revision_count": 0}
            ),
        )
    except Exception as error:
        fail_interaction(request_id=request_id, stage="workflow", error=error)
        raise
    answer = state["answer"].model_dump(mode="json")
    answer["request_id"] = request_id
    if "proposal" in state:
        answer["query"] = state["proposal"].model_dump(mode="json")
    if "validation" in state:
        answer["validation"] = state["validation"].model_dump(mode="json")
    if "result" in state:
        answer["result"] = state["result"].model_dump(mode="json")
        answer["evidence"] = state["result"].evidence
    answer["analysis_performed"] = [
        "discover_metadata",
        "route_question",
        "generate_sql",
        "validate_sql",
        "review_semantics",
    ] + (
        ["execute_readonly_query", "synthesize_result"]
        if "result" in state
        else ["synthesize_explanation"]
    )
    record_interaction(
        request_id=request_id,
        question=question,
        response=answer,
        conversation_id=conversation_id,
    )
    return answer
