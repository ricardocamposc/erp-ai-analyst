from app.db.synthetic import DATA_END, DATA_START, MONTHS, SEED, build_dataset


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
    assert MONTHS[0][0] == DATA_START
    assert MONTHS[-1][1] == DATA_END
    assert {row["business_key"] for row in rows["accounting_period"]} == {
        f"PERIOD-{period_start:%Y-%m}" for period_start, _ in MONTHS
    }


def test_every_temporal_domain_has_rows_in_each_generated_month() -> None:
    rows = build_dataset()
    expected_months = {period_start.strftime("%Y-%m") for period_start, _ in MONTHS}
    month_fields = {
        "sales_document": "document_date",
        "inventory_movement": "movement_date",
        "stock_balance": "balance_date",
        "purchase_order": "order_date",
        "goods_receipt": "receipt_date",
        "employee_payroll_summary": "period_start",
        "accounting_period": "period_start",
    }
    for table, field in month_fields.items():
        observed = {row[field].strftime("%Y-%m") for row in rows[table]}
        assert observed == expected_months, table

    assert all(row["document_date"] <= DATA_END for row in rows["sales_document"])
