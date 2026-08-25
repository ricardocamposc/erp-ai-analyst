"""Run Agentic Evaluation v2 through OpenAI, LangGraph, and LangSmith."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from time import perf_counter
from typing import Any

from app.agent.gateway import OpenAIGateway
from app.agent.graph import run_analysis
from app.tools.registry import ToolExecutionError, execute_tool

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "evaluation" / "cases.jsonl"
GROUND_TRUTH = ROOT / "evaluation" / "expected" / "ground-truth-v1.json"
RUNS = ROOT / "evaluation" / "runs"
NUMBER = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?")
FACT_ALIASES = {
    "gross margin": {"gross margin", "margen bruto"},
}


class InstrumentedOpenAIGateway(OpenAIGateway):
    """OpenAI gateway with per-run call accounting for evaluation evidence."""

    def __init__(self) -> None:
        super().__init__()
        self.model_call_count = 0

    def interpret(self, question: str):  # type: ignore[no-untyped-def]
        result = super().interpret(question)
        self.model_call_count += 1
        return result

    def plan(self, intent):  # type: ignore[no-untyped-def]
        result = super().plan(intent)
        self.model_call_count += 1
        return result

    def synthesize(self, question: str, results: list[dict[str, Any]]):
        result = super().synthesize(question, results)
        self.model_call_count += 1
        return result


def _cases() -> list[dict[str, Any]]:
    return [json.loads(line) for line in CASES.read_text().splitlines() if line.strip()]


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        flattened: dict[str, Any] = {}
        for key, item in value.items():
            flattened.update(_flatten(item, f"{prefix}.{key}" if prefix else key))
        return flattened
    return {prefix: value}


def _decimal(value: Any) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _normalize_fact_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value)).casefold()
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[_\-]+", " ", text)


def _fact_variants(fact: str) -> set[str]:
    normalized = _normalize_fact_text(fact)
    variants = {normalized}
    for key, aliases in FACT_ALIASES.items():
        normalized_aliases = {_normalize_fact_text(alias) for alias in aliases}
        if normalized in normalized_aliases:
            variants.update(normalized_aliases)
    return variants


def _calculation_matches(case: dict[str, Any], actual: dict[str, Any]) -> bool:
    results = {
        item.get("tool_name"): item.get("data", {})
        for item in actual.get("structured_data", [])
    }
    for expected in case.get("expected_calculations", []):
        observed = _flatten(results.get(expected["tool"], {})).get(expected["path"])
        expected_number = _decimal(expected["expected"])
        if expected_number is not None:
            if _decimal(observed) != expected_number:
                return False
        elif str(observed) != str(expected["expected"]):
            return False
    return True


def _key_fact_coverage(case: dict[str, Any], actual: dict[str, Any]) -> float:
    grounded_output = {
        "answer": actual.get("answer", ""),
        "structured_data": actual.get("structured_data", []),
        "evidence": actual.get("evidence", []),
    }
    haystack = _normalize_fact_text(
        json.dumps(grounded_output, ensure_ascii=False, sort_keys=True)
    )
    facts = [str(item) for item in case.get("expected_key_facts", [])]
    matched = sum(
        any(variant in haystack for variant in _fact_variants(fact))
        for fact in facts
    )
    return matched / len(facts) if facts else 1.0


def _numeric_claim_rate(actual: dict[str, Any]) -> tuple[int, int]:
    claims = NUMBER.findall(str(actual.get("answer", "")))
    supported = set(NUMBER.findall(json.dumps(actual.get("structured_data", []))))
    return sum(claim not in supported for claim in claims), len(claims)


def _failure_case(case: dict[str, Any]) -> dict[str, Any]:
    started = perf_counter()
    try:
        execute_tool(case["tool_name"], case.get("tool_arguments", {}))
    except ToolExecutionError:
        safe_failure = True
    else:
        safe_failure = False
    return {
        "status": "failed" if safe_failure else "completed",
        "actual_tools": [case["tool_name"]],
        "answer": "safe tool failure" if safe_failure else "unexpected success",
        "structured_data": [],
        "evidence": [],
        "latency_ms": round((perf_counter() - started) * 1000, 3),
        "tool_call_count": 1,
        "model_call_count": 0,
        "token_usage": None,
        "estimated_cost": None,
        "failure_safe": safe_failure,
    }


def _evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    started = perf_counter()
    gateway = InstrumentedOpenAIGateway()
    if case.get("evaluation_mode") in {"invalid_tool_arguments", "unknown_tool"}:
        actual = _failure_case(case)
    else:
        actual = run_analysis(case["question"], gateway, request_id=case["id"])
        actual["actual_tools"] = actual.get("analysis_performed", [])
        actual["latency_ms"] = round((perf_counter() - started) * 1000, 3)
        actual["tool_call_count"] = len(actual["actual_tools"])
        actual["model_call_count"] = gateway.model_call_count
        actual["token_usage"] = None
        actual["estimated_cost"] = None

    actual_tools = set(actual.get("actual_tools", []))
    expected_tools = set(case.get("expected_tools", []))
    forbidden_tools = set(case.get("forbidden_tools", []))
    tool_match = expected_tools.issubset(actual_tools) and not (
        actual_tools & forbidden_tools
    )
    fact_coverage = _key_fact_coverage(case, actual)
    unsupported, numeric_claims = _numeric_claim_rate(actual)
    status_match = actual.get("status") == case.get("expected_status")
    workflow_success = (
        bool(actual.get("failure_safe"))
        if case.get("evaluation_mode")
        else status_match and tool_match and actual.get("model_call_count", 0) > 0
    )
    relevant_tools = expected_tools | set(case.get("allowed_tools", []))
    unnecessary = actual_tools - relevant_tools
    return {
        "id": case["id"],
        "category": case["category"],
        "domain": case.get("domain", []),
        "expected_status": case.get("expected_status"),
        "actual_status": actual.get("status"),
        "status_match": status_match,
        "expected_tools": sorted(expected_tools),
        "actual_tools": sorted(actual_tools),
        "forbidden_tools_used": sorted(actual_tools & forbidden_tools),
        "tool_selection_match": tool_match,
        "calculation_correct": _calculation_matches(case, actual),
        "key_fact_coverage": round(fact_coverage, 4),
        "unsupported_quantitative_claims": unsupported,
        "quantitative_claims": numeric_claims,
        "unnecessary_tools": sorted(unnecessary),
        "workflow_success": workflow_success,
        "guardrail_success": case["category"] != "guardrail"
        or (status_match and tool_match),
        "cross_domain_success": case["category"] != "cross_domain"
        or (tool_match and status_match),
        "latency_ms": actual["latency_ms"],
        "model_call_count": actual["model_call_count"],
        "tool_call_count": actual["tool_call_count"],
        "token_usage": actual["token_usage"],
        "estimated_cost": actual["estimated_cost"],
        "answer": actual.get("answer", ""),
    }


def _rate(items: list[dict[str, Any]], key: str) -> float:
    return round(sum(bool(item[key]) for item in items) / len(items), 4) if items else 0.0


def _report(results: list[dict[str, Any]], mode: str, repetitions: int) -> dict[str, Any]:
    numeric_total = sum(item["quantitative_claims"] for item in results)
    numeric_unsupported = sum(item["unsupported_quantitative_claims"] for item in results)
    cross = [item for item in results if item["category"] == "cross_domain"]
    guard = [item for item in results if item["category"] == "guardrail"]
    single = [item for item in results if item["category"] == "single_domain"]
    resilience = [item for item in results if item["category"] == "resilience"]
    # Guardrail refusals are intentionally allowed to terminate before an LLM
    # call; only answerable analytical cases prove the agentic path.
    analytical = [
        item for item in results if item["category"] in {"single_domain", "cross_domain"}
    ]
    return {
        "evaluation": "ERP AI Analyst Agentic Evaluation v2",
        "mode": mode,
        "repetitions_per_case": repetitions,
        "dataset": "evaluation/cases.jsonl",
        "generated_at": datetime.now(UTC).isoformat(),
        "case_count": len(results),
        "execution_count": len(results),
        "distribution": {
            "single_domain": len(single),
            "cross_domain": len(cross),
            "guardrail": len(guard),
            "resilience": len(resilience),
        },
        "agentic_proof": {
            "analytical_execution_count": len(analytical),
            "analytical_runs_with_model_calls": sum(
                item["model_call_count"] > 0 for item in analytical
            ),
            "total_model_calls": sum(item["model_call_count"] for item in results),
            "langgraph_workflow": "app.agent.graph.run_analysis",
            "gateway": "OpenAIGateway",
            "langsmith_tracing": "enabled by LANGCHAIN_TRACING_V2/LANGCHAIN_API_KEY",
        },
        "metrics": {
            "tool_selection_accuracy": _rate(results, "tool_selection_match"),
            "calculation_correctness": _rate(results, "calculation_correct"),
            "key_fact_coverage": round(
                sum(item["key_fact_coverage"] for item in results) / len(results), 4
            ),
            "unsupported_quantitative_claim_rate": round(
                numeric_unsupported / numeric_total, 4
            )
            if numeric_total
            else 0.0,
            "unnecessary_tool_call_rate": round(
                sum(bool(item["unnecessary_tools"]) for item in results) / len(results),
                4,
            ),
            "successful_workflow_rate": _rate(results, "workflow_success"),
            "guardrail_success_rate": _rate(guard, "guardrail_success"),
            "cross_domain_success_rate": _rate(cross, "cross_domain_success"),
        },
        "operational": {
            "average_latency_ms": round(
                sum(item["latency_ms"] for item in results) / len(results), 3
            ),
            "model_call_count": sum(item["model_call_count"] for item in results),
            "tool_call_count": sum(item["tool_call_count"] for item in results),
            "token_usage": None,
            "estimated_cost": None,
        },
        "failures": [
            item["id"]
            for item in results
            if not item["workflow_success"]
            or not item["calculation_correct"]
            or item["key_fact_coverage"] < 1
        ],
        "results": results,
    }


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ERP AI Analyst — Agentic Evaluation v2",
        "",
        f"Mode: {report['mode']}",
        f"Executions: {report['execution_count']}",
        f"Repetitions per case: {report['repetitions_per_case']}",
        "",
        "## Agentic execution proof",
    ]
    for key, value in report["agentic_proof"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Metrics"])
    for key, value in report["metrics"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Failures"])
    lines.extend(f"- `{item}`" for item in report["failures"]) or lines.append("- None")
    lines.extend(
        [
            "",
            "## Method",
            "Each analytical case calls OpenAIGateway through the bounded LangGraph workflow. Registered tools remain deterministic; LangSmith tracing is controlled by the repository environment.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("smoke", "official"), default="smoke")
    args = parser.parse_args()
    cases = _cases()
    if len(cases) != 36:
        raise RuntimeError(f"Agentic v2 requires exactly 36 cases, found {len(cases)}")
    if not GROUND_TRUTH.exists():
        raise RuntimeError(f"missing ground truth: {GROUND_TRUTH}")
    repetitions = 1 if args.mode == "smoke" else 3
    results = [_evaluate_case(case) for _ in range(repetitions) for case in cases]
    report = _report(results, args.mode, repetitions)
    if report["agentic_proof"]["analytical_runs_with_model_calls"] != report["agentic_proof"]["analytical_execution_count"]:
        raise RuntimeError(
            "Agentic v2 aborted: at least one analytical case had zero OpenAI model calls"
        )
    RUNS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    stem = f"agentic-v2-{args.mode}-{stamp}"
    json_path = RUNS / f"{stem}.json"
    markdown_path = RUNS / f"{stem}.md"
    serialized = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    json_path.write_text(serialized)
    markdown_path.write_text(_markdown(report))
    (ROOT / "evaluation" / "results" / "latest-agentic-v2.json").write_text(serialized)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    print(f"Saved: {json_path}")
    print(f"Saved: {markdown_path}")


if __name__ == "__main__":
    main()
