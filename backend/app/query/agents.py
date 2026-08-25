"""Agent roles for the dynamic query workflow."""

from typing import Any, cast

from langchain_openai import ChatOpenAI

from app.agent.contracts import FinalAnswer
from app.core.config import get_settings
from app.query.contracts import (
    QueryMetadata,
    QueryProposal,
    QuestionRoute,
    ValidationResult,
    ValidatorReview,
)
from app.query.guardrails import validate_query
from app.query.provider import LocalERPQueryProvider
from app.query.tools import execute_readonly_query


class DynamicAgentGateway:
    """LLM roles used by the coordinator; execution remains outside this class."""

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        self.model = model or settings.openai_model
        self.api_key = settings.openai_api_key

    def _structured(self, schema: type[Any]) -> Any:
        return ChatOpenAI(
            model=self.model,
            temperature=0,
            api_key=self.api_key,
        ).with_structured_output(schema, method="function_calling")

    def analyze(self, question: str, metadata: QueryMetadata, feedback: list[str] | None = None) -> QueryProposal:
        prompt = (
            "You are the ERP query analyst. Generate a read-only PostgreSQL SELECT "
            "for the user's business question using only the supplied ERP metadata. "
            "Never write data, use unknown tables, invent columns, or claim facts not "
            "available in the result. Prefer aggregate results and explicit period filters. "
            "Always qualify physical columns with their table alias, especially in joins and "
            "nested queries; use the exact table and column names from metadata.columns. "
            "Use the available_periods and system_date in the metadata; never invent dates. "
            "Distinguish temporal intent precisely: 'este mes', 'mes actual', 'este año' "
            "and 'últimos meses' are relative to system_date and must use that date as the "
            "reference, even when the ERP has no rows for that period. 'último mes que tuvimos "
            "ventas', 'última venta' and similar wording means the latest period actually "
            "present in the relevant table. An explicit month or year such as '<mes> de <año>' "
            "must be queried as explicitly requested. If a relative system period has no data, "
            "return no rows or explain the absence; do not silently substitute the latest "
            "historical period. If a requested window is longer than available history, state "
            "that limitation in assumptions rather than fabricating missing months. "
            "Requests framed as historical, registered, or based on the data available in the "
            "ERP should use the relevant catalog history, not the runtime current month. "
            "If the user does not specify a date, month, year, relative window or number of "
            "periods, do not add a date predicate. In that case, historical means all rows "
            "available in the relevant ERP tables; available_periods describes the result "
            "coverage but is not an instruction to invent minimum or maximum date literals. "
            "For system-relative periods, use CURRENT_DATE or the runtime system_date; never "
            "write a fixed historical date range. "
            "For causal questions about a metric changing, query the relevant current and "
            "previous periods and measurable ERP drivers. Do not answer with generic business "
            "reasons; if the ERP result does not prove a cause, say that explicitly. "
            "Never place aggregate expressions such as SUM, AVG or COUNT in WHERE; use HAVING "
            "for aggregate filters or a subquery/CTE when the aggregate must be filtered. "
            "When combining period-based facts from different domains, use the catalog's "
            "period foreign keys or matching period dimensions; never join facts only on a "
            "shared cost center or other dimension if that can multiply rows or detach the "
            "metric from its period. "
            "When the user asks for a projection, forecast, estimate or annualization and "
            "only part of the target period is available, calculate a transparent estimate "
            "from the observed periods instead of rejecting the request. Return the observed "
            "period totals and the projected value, and state the assumption used, such as "
            "the observed-period average annualized to the requested horizon. Set "
            "analysis_mode=projection. For an annual projection, aggregate by observed month "
            "and calculate the observed-period count, observed total, observed average and "
            "annualized estimate (average multiplied by twelve) in SQL or a transparent CTE. "
            "Label estimated values as estimates; never present them as actual recorded facts. "
            "When the user asks for the last months, aggregate by month with DATE_TRUNC "
            "unless the user explicitly asks for individual days. When the catalog only "
            "contains employee-level aggregates such as employee_count and has no employee "
            "identity table or name column, do not invent a worker name or salary ranking; "
            "set needs_clarification=true and explain that the requested grain is not present. "
            "Never interpret a fact table business_key as a person, customer, supplier or "
            "product identity unless the metadata explicitly identifies it as that entity's "
            "identifier. "
            "Return the SQL candidate, referenced tables/columns, joins, metrics, filters "
            "and assumptions. If the question is ambiguous or the metadata is insufficient, "
            "set needs_clarification=true."
        )
        if feedback:
            prompt += " Previous validator feedback to address: " + "; ".join(feedback)
        result = self._structured(QueryProposal).invoke(
            [
                ("system", prompt),
                (
                    "human",
                    f"Question: {question}\n"
                    f"RUNTIME SYSTEM DATE (authoritative): {metadata.system_date}\n"
                    f"Metadata: {metadata.model_dump_json()}"
                ),
            ]
        )
        return cast(QueryProposal, result)

    def route_question(self, question: str) -> QuestionRoute:
        prompt = (
            "Classify the ERP user's request. Use data_query only when the answer "
            "requires reading ERP records or calculating a value from them. Use "
            "erp_concept for general ERP knowledge such as definitions, formulas, "
            "or how to determine a business metric without asking for current data. "
            "Use unsupported only for requests outside ERP analysis. Questions that "
            "ask why sales, payroll, costs, inventory or another ERP metric increased "
            "or decreased in a period are data_query requests: they require comparing "
            "ERP periods and identifying supported drivers. Never classify a question "
            "about a concrete ERP metric and period as unsupported just because it uses "
            "the word why. Examples: '¿Por qué disminuyeron las ventas este mes?' and "
            "'¿Cómo evolucionó el costo de nómina?' are data_query; '¿Qué es el costo "
            "de venta?' is erp_concept. Questions asking which employee earns the most, "
            "salary rankings, invoice counts, purchase orders, stock risk or sales by "
            "month are also data_query requests."
        )
        result = self._structured(QuestionRoute).invoke(
            [("system", prompt), ("human", f"Question: {question}")]
        )
        return cast(QuestionRoute, result)

    def answer_concept(self, question: str) -> FinalAnswer:
        prompt = (
            "Answer the conceptual ERP question clearly in the same language as the user. Explain the "
            "definition, formula or practical method requested. Do not invent "
            "company-specific values and do not claim that a database query was "
            "executed. Return a completed answer with no evidence when the question "
            "is general ERP knowledge."
        )
        response = self._structured(FinalAnswer).invoke(
            [("system", prompt), ("human", f"Question: {question}")]
        )
        return cast(FinalAnswer, response)

    def answer_unsupported(self, question: str) -> FinalAnswer:
        prompt = (
            "Explain in the same language as the user's question that this request is outside "
            "the ERP analyst's supported scope. Do not answer with invented facts, do not call "
            "ERP tools, and briefly state which ERP-oriented questions are supported. Return "
            "status unsupported and keep collection fields empty."
        )
        response = self._structured(FinalAnswer).invoke(
            [("system", prompt), ("human", f"Question: {question}")]
        )
        return cast(FinalAnswer, response)

    def review(
        self,
        proposal: QueryProposal,
        validation: ValidationResult,
        metadata: QueryMetadata | None = None,
        database_validated: bool = False,
        result: dict[str, Any] | None = None,
    ) -> ValidatorReview:
        pre_execution = result is None
        prompt = (
            "You are the ERP query validator. Check whether the candidate SQL answers "
            "the stated goal and whether the deterministic validation result leaves semantic "
            "issues. Never override a deterministic rejection. Approve only when the query "
            "is semantically aligned; otherwise provide precise revision instructions. Set "
            "blocking_issue=false for observations, caveats or data-coverage limitations "
            "that do not make the returned metric invalid. Set blocking_issue=true only for "
            "a real mismatch in entity, metric, relationship, grain or query meaning. Set "
            "blocking_scope=coverage for period availability or completeness observations; "
            "use entity, metric, relationship, grain or meaning for actual semantic gaps, "
            "and none when there is no issue. "
            "Before execution, do not block a query because the requested period extends "
            "beyond the rows currently present; that is a result-coverage concern and must "
            "be evaluated only after the read-only query returns. "
            "Interpret temporal language from the user, not from the latest database row. "
            "'este mes', 'mes actual', 'este año' and 'últimos meses' are relative to the "
            "runtime system_date in metadata. 'último mes que tuvimos ventas' and 'última "
            "venta' refer to the latest available ERP data. An explicit month or year must "
            "be honored exactly. Do not substitute the latest historical period for a system "
            "relative period with no data. A date earlier than metadata.system_date is "
            "historical and valid; never call a past period future merely because it differs "
            "from the runtime date. Explicit historical periods and requests for registered "
            "historical data must be evaluated against the ERP catalog, not the current calendar."
            " If no temporal scope appears in the user's question, preserve the full catalog "
            "history and do not infer a date range from available_periods. "
            " The database validation result is authoritative: when database_validated is "
            "true, PostgreSQL has already accepted the SQL syntax, tables, columns, joins "
            "and grouping. Do not reject it for temporal wording, fixed historical dates, "
            "or a different system date. If EXECUTION_RESULT contains rows and the SQL "
            "was accepted by PostgreSQL, treat those rows as authoritative evidence and "
            "approve unless the requested metric or entity is genuinely absent. A date "
            "literal one day after the maximum period is valid as an exclusive upper bound; "
            "do not reject that SQL merely because the literal itself exceeds the maximum "
            "observed date."
            " Keep semantic review mandatory for entity or metric mismatches, but do not "
            "reject a semantically aligned proposal solely because a date boundary is "
            "exclusive, the history is shorter than twelve months, or the data is historical. "
            "Do not infer that a month is incomplete merely because the maximum observed "
            "transaction date is before its calendar end. Holidays, weekends, closures or "
            "zero-transaction days are valid explanations; observed rows remain valid evidence. "
            "Never block a total or comparison for that reason. When PostgreSQL accepted the "
            "statement and EXECUTION_RESULT contains rows, treat the temporal scope and date "
            "literals as already resolved by the analyst and database. Do not compare them to "
            "the runtime date and do not generate a rejection about past, future, historical, "
            "current or incomplete periods. Review only whether the returned entity, metric, "
            "relationships and grain answer the business goal."
            " A projection, forecast or annualization is valid with partial observations; "
            "do not require twelve months of actual data. When proposal analysis_mode is "
            "projection, review the calculation and assumptions rather than requiring a full "
            "year of observations."
            " A projection, forecast or annualization is valid with partial observations; "
            "do not require twelve months of actual data. Review whether the calculation and "
            "assumptions are represented, not whether the observed history is a complete year."
        )
        if pre_execution:
            prompt += (
                " This is the pre-execution gate. Do not assess whether the database has "
                "rows for the requested range or whether the range covers a complete year "
                "or month. Those are result-coverage observations, not blocking semantic "
                "issues. Validate only the requested entity, metric, grain, relationships "
                "and meaning of the SQL."
            )
        period_summary = "; ".join(
            f"{table}: {details.get('minimum')}..{details.get('maximum')}"
            for table, details in (metadata.available_periods.items() if metadata else [])
        )
        temporal_interpretation = (
            "Use metadata.system_date for system-relative periods. Use available_periods "
            "only for questions explicitly asking for the latest period with ERP data."
        )
        review_metadata = (
            metadata.model_copy(update={"available_periods": {}, "system_date": None})
            if metadata is not None and (pre_execution or result is not None)
            else metadata
        )
        result = self._structured(ValidatorReview).invoke(
            [
                ("system", prompt),
                (
                    "human",
                    f"Proposal: {proposal.model_dump_json()}\n"
                    f"Deterministic validation: {validation.model_dump_json()}\n"
                    f"DATABASE_EXPLAIN_PASSED: {database_validated}\n"
                    f"EXECUTION_RESULT: {(result if result is not None else 'not executed')}\n"
                    f"ERP PERIODS AND SYSTEM DATE: {'coverage is handled by the analyst; temporal scope is not reviewed here' if result is not None else period_summary if not pre_execution else 'coverage not evaluated before execution'}; system_date=None\n"
                    f"TEMPORAL INTERPRETATION: {temporal_interpretation}\n"
                    f"Available ERP metadata: {(review_metadata.model_dump_json() if review_metadata else 'not supplied')}"
                ),
            ]
        )
        return cast(ValidatorReview, result)

    def synthesize(self, question: str, result: dict[str, Any]) -> FinalAnswer:
        prompt = (
            "Answer only from the approved deterministic query result. Preserve numbers, "
            "state the period and distinguish facts from recommendations. If there are no "
            "rows, say that no records matched; do not invent an explanation. For comparison "
            "questions, determine the direction from the returned numbers: if current is "
            "greater than previous, say it increased; if current is lower, say it decreased. "
            "If the user's premise is false, state that clearly and do not reverse the periods."
            " Whenever a result is grouped or compared by month, year, period or date, "
            "include the month and year explicitly for every value; never present an unlabeled "
            "monthly number. Use the result columns as the authoritative period labels."
            " For a question that presupposes a decrease, first compare the returned current "
            "and previous values; if current is greater, begin by saying that sales did not "
            "decrease. Never write that they decreased when the result shows an increase. "
            "If the requested window exceeds the available rows, answer using the available "
            "history and explicitly state that it is a partial historical window. A partial "
            "observed month is still reportable; do not replace the result with an error. "
            "For projections or annualizations, report the projected value as an estimate and "
            "state the calculation assumption briefly; do not say that projection is impossible "
            "solely because fewer than twelve months are observed. Use the projection fields "
            "returned by the query as authoritative and distinguish observed totals from the "
            "annualized estimate. "
            "The application renders result rows in a table below the answer. Do not repeat "
            "the result set, row values, bullet lists, or table contents in answer; write only "
            "a concise introductory sentence and any necessary interpretation or caveat."
        )
        response = self._structured(FinalAnswer).invoke(
            [("system", prompt), ("human", f"Question: {question}\nResult: {result}")]
        )
        return cast(FinalAnswer, response)

    def synthesize_insufficient(self, question: str, reasons: list[str]) -> FinalAnswer:
        prompt = (
            "Explain in the same language as the user's question why the ERP request could not be answered from the "
            "available catalog. Be explicit about missing data grain, unavailable "
            "tables or columns, SQL validation errors, or the need for clarification. "
            "Do not invent a value, employee, cause or database result. Return status "
            "insufficient_data and preserve the reasons as warnings."
        )
        response = self._structured(FinalAnswer).invoke(
            [("system", prompt), ("human", f"Question: {question}\nReasons: {reasons}")]
        )
        return cast(FinalAnswer, response)

    def synthesize_no_data(
        self, question: str, system_date: str, available_periods: dict[str, Any]
    ) -> FinalAnswer:
        prompt = (
            "Answer in the same language as the user's question that no ERP records are available for the system-relative "
            "period requested. Do not mention SQL errors, validation failures or internal "
            "agents. Explain that the question refers to the current system period, give "
            "the system date, and distinguish it from the latest historical period with "
            "data. Do not substitute historical data unless the user asks for it. Return "
            "status insufficient_data, with a concise warning."
        )
        response = self._structured(FinalAnswer).invoke(
            [
                ("system", prompt),
                (
                    "human",
                    f"Question: {question}\nSystem date: {system_date}\n"
                    f"Available ERP periods: {available_periods}",
                ),
            ]
        )
        return cast(FinalAnswer, response)

    def adjudicate_review(
        self,
        proposal: QueryProposal,
        validation: ValidationResult,
        review: ValidatorReview,
        metadata: QueryMetadata,
        result: dict[str, Any] | None = None,
    ) -> ValidatorReview:
        prompt = (
            "You are the senior ERP semantic adjudicator. Review the first validator's "
            "objections against the exact SQL, the PostgreSQL validation status and the "
            "returned result. Keep a rejection only when the query cannot answer "
            "the requested entity or metric, uses an unavailable grain, or contradicts the "
            "question. Set blocking_issue=false for non-blocking observations or coverage "
            "limitations; reserve blocking_issue=true for a genuine semantic mismatch. Set "
            "blocking_scope=coverage for period observations and entity, metric, relationship, "
            "grain or meaning for genuine semantic mismatches. "
            "Do not assess temporal alignment in this stage. Dates, historical ranges, "
            "system-relative periods, incomplete coverage and date literals are outside the "
            "adjudicator's blocking authority. PostgreSQL already accepted the statement and "
            "the returned rows are authoritative evidence. Never reject a non-empty result "
            "because a date is before, after or different from the runtime date. Do not "
            "invent a current date or require a full calendar year. Preserve a rejection only "
            "for a genuine entity, metric, relationship, grain or meaning mismatch, with "
            "specific revision instructions."
        )
        semantic_metadata = metadata.model_copy(update={"available_periods": {}, "system_date": None})
        result = self._structured(ValidatorReview).invoke(
            [
                ("system", prompt),
                (
                    "human",
                    f"Proposal: {proposal.model_dump_json()}\n"
                    f"PostgreSQL validation: {validation.model_dump_json()}\n"
                    f"First review: {review.model_dump_json()}\n"
                    f"Execution result: {(result if result is not None else 'not executed')}\n"
                    f"ERP schema metadata (temporal catalog omitted for this semantic review): {semantic_metadata.model_dump_json()}",
                ),
            ]
        )
        return cast(ValidatorReview, result)


class DynamicCoordinator:
    """Coordinates analyst, validator, guardrails and execution stages."""

    def __init__(self, provider: LocalERPQueryProvider | None = None, gateway: DynamicAgentGateway | None = None) -> None:
        self.provider = provider or LocalERPQueryProvider()
        self.gateway = gateway or DynamicAgentGateway()

    def run(self, question: str, request_id: str, max_revisions: int = 2) -> dict[str, Any]:
        metadata = self.provider.metadata()
        feedback: list[str] = []
        proposal: QueryProposal | None = None
        validation: ValidationResult | None = None
        for _attempt in range(max_revisions + 1):
            proposal = self.gateway.analyze(question, metadata, feedback)
            validation = validate_query(proposal, metadata)
            review = self.gateway.review(proposal, validation)
            if validation.status == "approved" and review.approved:
                result = execute_readonly_query(self.provider, proposal, 500)
                answer = self.gateway.synthesize(question, result.model_dump(mode="json"))
                return {**answer.model_dump(mode="json"), "request_id": request_id, "query": proposal.model_dump(mode="json"), "validation": validation.model_dump(mode="json"), "result": result.model_dump(mode="json")}
            feedback = validation.reasons + review.semantic_issues + review.revision_instructions
        return {"answer": "No se pudo aprobar una consulta segura y semánticamente suficiente.", "status": "insufficient_data", "warnings": feedback, "request_id": request_id}
