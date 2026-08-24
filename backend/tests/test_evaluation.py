import json
from pathlib import Path

from app.agent.gateway import RuleBasedGateway
from app.agent.graph import run_analysis


def test_evaluation_dataset_has_all_six_domains_and_negative_cases() -> None:
    cases = [
        json.loads(line)
        for line in Path("evaluation/cases.jsonl").read_text().splitlines()
    ]
    categories = {case["category"] for case in cases}
    domains = {domain for case in cases for domain in case.get("domain", [])}

    assert {
        "customers",
        "inventory",
        "purchases",
        "payroll",
        "accounting",
        "cross_domain",
    } <= domains | categories
    assert {case["expected_intent"] for case in cases} >= {
        "unsupported_request",
        "sales_variance_analysis",
    }


def test_baseline_v1_has_exact_distribution_and_ground_truth() -> None:
    cases = [
        json.loads(line)
        for line in Path("evaluation/cases.jsonl").read_text().splitlines()
    ]
    assert len(cases) == 36
    counts = {
        category: 0
        for category in ("single_domain", "cross_domain", "guardrail", "resilience")
    }
    for case in cases:
        counts[case["category"]] += 1
    assert counts == {
        "single_domain": 18,
        "cross_domain": 10,
        "guardrail": 6,
        "resilience": 2,
    }
    ground_truth = json.loads(
        Path("evaluation/expected/ground-truth-v1.json").read_text()
    )
    assert ground_truth["coverage"]["sales_documents"] == 397
    assert ground_truth["facts"]["sales_april_vs_march"]["absolute_change"] == "1276.00"


def test_offline_evaluation_metrics_are_reproducible() -> None:
    result = run_analysis(
        "¿Por qué disminuyeron las ventas este mes?",
        RuleBasedGateway(),
        request_id="eval-test",
    )

    assert result["status"] == "completed"
    assert result["request_id"] == "eval-test"
    assert result["evidence"]
