"""Load and validate the deterministic Slice 1 dataset."""

from typing import Any

from sqlalchemy import MetaData, Table, text
from sqlalchemy.engine import Connection, Engine

from app.db.synthetic import build_dataset

BASE_TABLES = (
    "customer",
    "product",
    "salesperson",
    "supplier",
    "cost_center",
    "payroll_concept",
)


def _insert_base(
    connection: Connection,
    tables: dict[str, Table],
    rows: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, int]]:
    ids: dict[str, dict[str, int]] = {}
    for name in BASE_TABLES:
        connection.execute(tables[name].insert(), rows[name])
        ids[name] = {
            row.business_key: row.id
            for row in connection.execute(tables[name].select())
        }
    return ids


def _db_values(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in row.items()
        if not key.endswith("_key") or key == "business_key"
    }


def seed_database(engine: Engine) -> None:
    metadata = MetaData()
    metadata.reflect(bind=engine)
    tables = {name: metadata.tables[name] for name in metadata.tables}
    rows = build_dataset()
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE account_balance, accounting_period, payroll_summary_line, employee_payroll_summary, goods_receipt_line, goods_receipt, purchase_order_line, purchase_order, stock_balance, inventory_movement, sales_document_line, sales_document, payroll_concept, cost_center, supplier, salesperson, product, customer RESTART IDENTITY CASCADE"
            )
        )
        ids = _insert_base(connection, tables, rows)
        for row in rows["sales_document"]:
            values = _db_values(row)
            values["customer_id"] = ids["customer"][row["customer_key"]]
            values["salesperson_id"] = ids["salesperson"][row["salesperson_key"]]
            connection.execute(tables["sales_document"].insert(), values)
        sales_ids = {
            row.business_key: row.id
            for row in connection.execute(tables["sales_document"].select())
        }
        for row in rows["sales_document_line"]:
            values = _db_values(row)
            values["sales_document_id"] = sales_ids[row["sales_document_key"]]
            values["product_id"] = ids["product"][row["product_key"]]
            connection.execute(tables["sales_document_line"].insert(), values)
        for row in rows["inventory_movement"]:
            values = _db_values(row)
            values["product_id"] = ids["product"][row["product_key"]]
            connection.execute(tables["inventory_movement"].insert(), values)
        for row in rows["stock_balance"]:
            values = _db_values(row)
            values["product_id"] = ids["product"][row["product_key"]]
            connection.execute(tables["stock_balance"].insert(), values)
        for row in rows["purchase_order"]:
            values = _db_values(row)
            values["supplier_id"] = ids["supplier"][row["supplier_key"]]
            connection.execute(tables["purchase_order"].insert(), values)
        po_ids = {
            row.business_key: row.id
            for row in connection.execute(tables["purchase_order"].select())
        }
        for row in rows["purchase_order_line"]:
            values = _db_values(row)
            values["purchase_order_id"] = po_ids[row["purchase_order_key"]]
            values["product_id"] = ids["product"][row["product_key"]]
            connection.execute(tables["purchase_order_line"].insert(), values)
        pol_ids = {
            row.business_key: row.id
            for row in connection.execute(tables["purchase_order_line"].select())
        }
        for row in rows["goods_receipt"]:
            values = _db_values(row)
            values["purchase_order_id"] = po_ids[row["purchase_order_key"]]
            connection.execute(tables["goods_receipt"].insert(), values)
        gr_ids = {
            row.business_key: row.id
            for row in connection.execute(tables["goods_receipt"].select())
        }
        for row in rows["goods_receipt_line"]:
            values = _db_values(row)
            values["goods_receipt_id"] = gr_ids[row["goods_receipt_key"]]
            values["purchase_order_line_id"] = pol_ids[row["purchase_order_line_key"]]
            connection.execute(tables["goods_receipt_line"].insert(), values)
        for row in rows["employee_payroll_summary"]:
            values = _db_values(row)
            values["cost_center_id"] = ids["cost_center"][row["cost_center_key"]]
            connection.execute(tables["employee_payroll_summary"].insert(), values)
        pay_ids = {
            row.business_key: row.id
            for row in connection.execute(tables["employee_payroll_summary"].select())
        }
        for row in rows["payroll_summary_line"]:
            values = _db_values(row)
            values["payroll_summary_id"] = pay_ids[row["payroll_summary_key"]]
            values["payroll_concept_id"] = ids["payroll_concept"][
                row["payroll_concept_key"]
            ]
            connection.execute(tables["payroll_summary_line"].insert(), values)
        for row in rows["accounting_period"]:
            values = _db_values(row)
            connection.execute(tables["accounting_period"].insert(), values)
        period_ids = {
            row.business_key: row.id
            for row in connection.execute(tables["accounting_period"].select())
        }
        for row in rows["account_balance"]:
            values = _db_values(row)
            values["accounting_period_id"] = period_ids[row["accounting_period_key"]]
            values["cost_center_id"] = ids["cost_center"].get(row["cost_center_key"])
            connection.execute(tables["account_balance"].insert(), values)


def validate_database(engine: Engine) -> list[str]:
    """Return validation errors; an empty list means the dataset is coherent."""
    errors: list[str] = []
    with engine.connect() as connection:
        for table in (
            "customer",
            "product",
            "sales_document",
            "sales_document_line",
            "inventory_movement",
            "stock_balance",
            "supplier",
            "purchase_order",
            "purchase_order_line",
            "goods_receipt",
            "goods_receipt_line",
            "employee_payroll_summary",
            "payroll_summary_line",
            "accounting_period",
            "account_balance",
        ):
            count = connection.execute(
                text(f"SELECT count(*) FROM {table}")
            ).scalar_one()
            if count == 0:
                errors.append(f"{table} is empty")
        bad_sales = connection.execute(
            text(
                "SELECT count(*) FROM sales_document_line WHERE quantity <= 0 OR unit_price < 0"
            )
        ).scalar_one()
        if bad_sales:
            errors.append("invalid sales arithmetic inputs")
        bad_receipts = connection.execute(
            text(
                "SELECT count(*) FROM goods_receipt_line gl JOIN purchase_order_line pl ON pl.id = gl.purchase_order_line_id WHERE gl.received_quantity > pl.ordered_quantity"
            )
        ).scalar_one()
        if bad_receipts:
            errors.append("receipt quantity exceeds ordered quantity")
        bad_payroll = connection.execute(
            text(
                "SELECT count(*) FROM employee_payroll_summary s WHERE s.total_cost <> (SELECT COALESCE(sum(l.amount), 0) FROM payroll_summary_line l WHERE l.payroll_summary_id = s.id)"
            )
        ).scalar_one()
        if bad_payroll:
            errors.append("payroll summary does not equal line total")
        march_stockout = connection.execute(
            text(
                "SELECT count(*) FROM stock_balance sb JOIN product p ON p.id = sb.product_id WHERE p.business_key = 'P-104' AND sb.balance_date = DATE '2025-03-01' AND sb.quantity = 0"
            )
        ).scalar_one()
        if march_stockout != 1:
            errors.append("S2 stockout control missing")
        bad_stock = connection.execute(
            text(
                "SELECT count(*) FROM stock_balance sb WHERE sb.quantity <> (SELECT COALESCE(sum(im.quantity), 0) FROM inventory_movement im WHERE im.product_id = sb.product_id AND im.movement_date <= sb.balance_date)"
            )
        ).scalar_one()
        if bad_stock:
            errors.append("stock balances do not reconcile to movements")
    return errors
