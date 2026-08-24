from app.db.synthetic import SEED, build_dataset


def test_synthetic_generation_is_deterministic() -> None:
    assert SEED == 20250824
    assert build_dataset() == build_dataset()


def test_slice_one_scenarios_are_present_in_generated_rows() -> None:
    rows = build_dataset()

    assert any(
        row["product_key"] == "P-104" and row["quantity"] == 0
        for row in rows["stock_balance"]
    )
    assert any(
        row["business_key"] == "PO-02-P-104" and row["status"] == "partial"
        for row in rows["purchase_order"]
    )
    assert any(
        row["payroll_concept_key"] == "PC-OT" for row in rows["payroll_summary_line"]
    )
    assert {row["business_key"] for row in rows["accounting_period"]} == {
        "PERIOD-2025-01",
        "PERIOD-2025-02",
        "PERIOD-2025-03",
        "PERIOD-2025-04",
    }
