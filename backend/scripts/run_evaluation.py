"""Run Evaluation Baseline v1.0 against the deterministic ERP workflow."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from time import perf_counter
from typing import Any

from app.agent.gateway import RuleBasedGateway
from app.agent.graph import run_analysis
from app.tools.registry import ToolExecutionError, execute_tool

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evaluation" / "cases.jsonl"
GROUND_TRUTH = ROOT / "evaluation" / "expected" / "ground-truth-v1.json"
RUNS = ROOT / "evaluation" / "runs"
NUMBER = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?")


def _cases() -> list[dict[str, Any]]:
    return [json.loads(line) for line in CASES.read_text().splitlines() if line.strip()]


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            result.update(_flatten(item, f"{prefix}.{key}" if prefix else key))
        return result
    return {prefix: value}


def _decimal(value: Any) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _calculation_matches(case: dict[str, Any], actual: dict[str, Any]) -> bool:
    results = {
        item.get("tool_name"): item.get("data", {})
        for item in actual.get("structured_data", [])
    }
    for expected in case.get("expected_calculations", []):
        values = _flatten(results.get(expected["tool"], {}))
        observed = values.get(expected["path"])
        expected_number = _decimal(expected["expected"])
        if expected_number is not None:
            if _decimal(observed) != expected_number:
                return False
        elif str(observed) != str(expected["expected"]):
            return False
    return True


def _key_fact_coverage(case: dict[str, Any], actual: dict[str, Any]) -> float:
    haystack = json.dumps(actual, ensure_ascii=False, sort_keys=True).lower()
    facts = [str(item).lower() for item in case.get("expected_key_facts", [])]
    return sum(fact in haystack for fact in facts) / len(facts) if facts else 1.0


def _numeric_claim_rate(actual: dict[str, Any]) -> tuple[int, int]:
    answer = str(actual.get("answer", ""))
    claims = NUMBER.findall(answer)
    if not claims:
        return 0, 0
    supported = set(NUMBER.findall(json.dumps(actual.get("structured_data", []))))
    unsupported = sum(claim not in supported for claim in claims)
    return unsupported, len(claims)


def _failure_case(case: dict[str, Any]) -> dict[str, Any]:
    started = perf_counter()
    try:
        execute_tool(case["tool_name"], case.get("tool_arguments", {}))
        safe_failure = False
    except ToolExecutionError:
        safe_failure = True
    latency_ms = round((perf_counter() - started) * 1000, 3)
    return {
        "status": "failed" if safe_failure else "completed",
        "actual_tools": [case["tool_name"]],
        "answer": "safe tool failure" if safe_failure else "unexpected success",
        "structured_data": [],
        "evidence": [],
        "latency_ms": latency_ms,
        "tool_call_count": 1,
        "model_call_count": 0,
        "token_usage": None,
        "estimated_cost": None,
        "failure_safe": safe_failure,
    }


def _evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    started = perf_counter()
    if case.get("evaluation_mode") in {"invalid_tool_arguments", "unknown_tool"}:
        actual = _failure_case(case)
    else:
        actual = run_analysis(
            case["question"], RuleBasedGateway(), request_id=case["id"]
        )
        actual["actual_tools"] = actual.get("analysis_performed", [])
        actual["latency_ms"] = round((perf_counter() - started) * 1000, 3)
        actual["tool_call_count"] = len(actual["actual_tools"])
        actual["model_call_count"] = 0
        actual["token_usage"] = None
        actual["estimated_cost"] = None

    actual_tools = set(actual.get("actual_tools", []))
    expected_tools = set(case.get("expected_tools", []))
    forbidden_tools = set(case.get("forbidden_tools", []))
    tool_match = expected_tools.issubset(actual_tools) and not (
        actual_tools & forbidden_tools
    )
    fact_coverage = _key_fact_coverage(case, actual)
    calculation_match = _calculation_matches(case, actual)
    unsupported_claims, numeric_claims = _numeric_claim_rate(actual)
    status_match = actual.get("status") == case.get("expected_status")
    if case.get("evaluation_mode"):
        workflow_success = bool(actual.get("failure_safe"))
    else:
        workflow_success = status_match and tool_match
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
        "calculation_correct": calculation_match,
        "key_fact_coverage": round(fact_coverage, 4),
        "unsupported_quantitative_claims": unsupported_claims,
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
    return round(sum(bool(item[key]) for item in items) / len(items), 4)


def _report(results: list[dict[str, Any]], version: str) -> dict[str, Any]:
    numeric_total = sum(item["quantitative_claims"] for item in results)
    numeric_unsupported = sum(
        item["unsupported_quantitative_claims"] for item in results
    )
    cross = [item for item in results if item["category"] == "cross_domain"]
    guard = [item for item in results if item["category"] == "guardrail"]
    single = [item for item in results if item["category"] == "single_domain"]
    resilience = [item for item in results if item["category"] == "resilience"]
    return {
        "baseline": f"ERP AI Analyst Evaluation Baseline {version}",
        "dataset": "evaluation/cases.jsonl",
        "generated_at": datetime.now(UTC).isoformat(),
        "case_count": len(results),
        "distribution": {
            "single_domain": len(single),
            "cross_domain": len(cross),
            "guardrail": len(guard),
            "resilience": len(resilience),
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
            "token_usage": None,
            "estimated_cost": None,
            "model_call_count": sum(item["model_call_count"] for item in results),
            "tool_call_count": sum(item["tool_call_count"] for item in results),
        },
        "failures": [
            {
                "id": item["id"],
                "category": item["category"],
                "status_match": item["status_match"],
                "tool_selection_match": item["tool_selection_match"],
                "key_fact_coverage": item["key_fact_coverage"],
                "unnecessary_tools": item["unnecessary_tools"],
            }
            for item in results
            if not item["workflow_success"]
            or not item["calculation_correct"]
            or item["key_fact_coverage"] < 1
        ],
        "results": results,
    }


def _markdown(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    dist = report["distribution"]
    op = report["operational"]
    lines = [
        f"# ERP AI Analyst — Evaluation Baseline {report['baseline'].rsplit(' ', 1)[-1]}",
        "",
        f"Total cases: {report['case_count']}",
        f"Distribution: {dist['single_domain']} single-domain, {dist['cross_domain']} cross-domain, {dist['guardrail']} guardrail, {dist['resilience']} resilience.",
        "",
        "## Metrics",
    ]
    for key, value in metrics.items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Operational",
            f"- Average latency: {op['average_latency_ms']} ms",
            f"- Model calls: {op['model_call_count']}",
            f"- Tool calls: {op['tool_call_count']}",
            "- Token usage: not available in offline deterministic mode",
            "- Estimated cost: not available in offline deterministic mode",
            "",
            "## Failures and regressions",
        ]
    )
    failures = report["failures"]
    if failures:
        for failure in failures:
            lines.append(
                f"- `{failure['id']}`: {json.dumps(failure, ensure_ascii=False)}"
            )
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Method",
            "The run uses RuleBasedGateway, typed tools, and the PostgreSQL database from backend/.env. It performs no OpenAI calls and no writes.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="v1.0")
    args = parser.parse_args()
    cases = _cases()
    if len(cases) != 36:
        raise RuntimeError(f"baseline requires exactly 36 cases, found {len(cases)}")
    if not GROUND_TRUTH.exists():
        raise RuntimeError(f"missing ground truth: {GROUND_TRUTH}")
    results = [_evaluate_case(case) for case in cases]
    report = _report(results, args.version)
    RUNS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    version_slug = args.version.lower().replace(".", "")
    json_path = RUNS / f"baseline-{version_slug}-{stamp}.json"
    markdown_path = RUNS / f"baseline-{version_slug}-{stamp}.md"
    serialized = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    json_path.write_text(serialized)
    markdown_path.write_text(_markdown(report))
    (ROOT / "evaluation" / "results" / "latest.json").write_text(serialized)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    print(f"Saved: {json_path}")
    print(f"Saved: {markdown_path}")


if __name__ == "__main__":
    main()
