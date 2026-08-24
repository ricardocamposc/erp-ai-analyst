"""Real bounded LangGraph workflow for ERP analysis."""

from datetime import datetime
from typing import Any, cast
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from app.agent.contracts import FinalAnswer
from app.agent.gateway import ModelGateway, OpenAIGateway
from app.agent.state import AnalysisState
from app.observability.logging import log_event
from app.observability.tracing import trace_tool
from app.tools.registry import ToolExecutionError, execute_tool

MAX_ITERATIONS = 6
MAX_RETRIES = 1


def build_graph(gateway: ModelGateway | None = None) -> Any:
    active_gateway = gateway or OpenAIGateway()

    def interpret(state: AnalysisState) -> dict[str, Any]:
        log_event("workflow.interpret", state["request_id"])
        return {"intent": active_gateway.interpret(state["question"])}

    def plan(state: AnalysisState) -> dict[str, Any]:
        intent = state["intent"]
        log_event("workflow.plan", state["request_id"], intent=intent.intent)
        return {
            "remaining_plan": active_gateway.plan(intent),
            "warnings": [intent.warning] if intent.warning else [],
        }

    def execute_next(state: AnalysisState) -> dict[str, Any]:
        plan_items = list(state.get("remaining_plan", []))
        if not plan_items:
            return {}
        call = plan_items.pop(0)
        history = list(state.get("tool_history", []))
        evidence = list(state.get("evidence", []))
        warnings = list(state.get("warnings", []))
        try:
            with trace_tool(state["request_id"], call.tool_name, call.arguments):
                result = execute_tool(call.tool_name, call.arguments)
            dumped = result.model_dump(mode="json")
            history.append(
                {"tool_name": call.tool_name, "purpose": call.purpose, "result": dumped}
            )
            evidence.extend(result.evidence)
        except ToolExecutionError as error:
            warnings.append(str(error))
            history.append(
                {
                    "tool_name": call.tool_name,
                    "purpose": call.purpose,
                    "error": "safe tool failure",
                }
            )
        return {
            "remaining_plan": plan_items,
            "tool_history": history,
            "evidence": evidence,
            "warnings": warnings,
            "iteration_count": state.get("iteration_count", 0) + 1,
        }

    def route(state: AnalysisState) -> str:
        if (
            state.get("remaining_plan")
            and state.get("iteration_count", 0) < MAX_ITERATIONS
        ):
            return "execute"
        return "synthesize"

    def synthesize(state: AnalysisState) -> dict[str, Any]:
        intent = state["intent"]
        if not intent.supported:
            answer = FinalAnswer(
                answer="No puedo ejecutar esa solicitud dentro del alcance de ERP AI Analyst.",
                warnings=list(state.get("warnings", [])),
                status="unsupported",
            )
        else:
            answer = active_gateway.synthesize(
                state["question"],
                [
                    item["result"]
                    for item in state.get("tool_history", [])
                    if "result" in item
                ],
            )
            answer = answer.model_copy(
                update={
                    "warnings": list(
                        dict.fromkeys(answer.warnings + state.get("warnings", []))
                    ),
                    "evidence": state.get("evidence", []) or answer.evidence,
                    "analysis_performed": [
                        item["tool_name"]
                        for item in state.get("tool_history", [])
                        if "result" in item
                    ],
                    "structured_data": [
                        {
                            "tool_name": item["tool_name"],
                            "data": item["result"].get("data", {}),
                        }
                        for item in state.get("tool_history", [])
                        if "result" in item
                    ],
                }
            )
        return {"final_answer": answer}

    builder = StateGraph(AnalysisState)
    builder.add_node("interpret", interpret)
    builder.add_node("plan", plan)
    builder.add_node("execute", execute_next)
    builder.add_node("synthesize", synthesize)
    builder.add_edge(START, "interpret")
    builder.add_edge("interpret", "plan")
    builder.add_edge("plan", "execute")
    builder.add_conditional_edges(
        "execute", route, {"execute": "execute", "synthesize": "synthesize"}
    )
    builder.add_edge("synthesize", END)
    return builder.compile()


def run_analysis(
    question: str, gateway: ModelGateway | None = None, request_id: str | None = None
) -> dict[str, Any]:
    graph = build_graph(gateway)
    active_request_id = request_id or str(uuid4())
    log_event("workflow.start", active_request_id)
    state = cast(
        dict[str, Any],
        graph.invoke(
            {
                "request_id": active_request_id,
                "question": question,
                "tool_history": [],
                "evidence": [],
                "warnings": [],
                "errors": [],
                "iteration_count": 0,
                "retry_count": 0,
            }
        ),
    )
    final = cast(dict[str, Any], state["final_answer"].model_dump(mode="json"))
    final["request_id"] = state["request_id"]
    final["execution_timestamp"] = datetime.utcnow().isoformat() + "Z"
    log_event("workflow.complete", active_request_id, status=final.get("status"))
    return final
