"""Deterministic synthetic canonical ERP dataset for Slice 1."""

from datetime import date
from decimal import Decimal
from typing import Any

SEED = 20250824
CURRENCY = "USD"
MONTHS = (
    (date(2025, 1, 1), date(2025, 1, 31)),
    (date(2025, 2, 1), date(2025, 2, 28)),
    (date(2025, 3, 1), date(2025, 3, 31)),
    (date(2025, 4, 1), date(2025, 4, 30)),
)


def _money(value: int | float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def build_dataset() -> dict[str, list[dict[str, Any]]]:
    """Return stable rows; no database or production analytics service is used."""
    customers = [
        {
            "business_key": "C-001",
            "name": "Northwind Retail",
            "segment": "retail",
            "active": True,
        },
        {
            "business_key": "C-002",
            "name": "Andes Market",
            "segment": "retail",
            "active": True,
        },
        {
            "business_key": "C-003",
            "name": "Coastal Hotels",
            "segment": "hospitality",
            "active": True,
        },
        {
            "business_key": "C-004",
            "name": "New Horizon",
            "segment": "services",
            "active": True,
        },
    ]
    products = [
        {
            "business_key": "P-100",
            "name": "Standard Pack",
            "category": "core",
            "unit": "unit",
            "standard_cost": _money(12),
        },
        {
            "business_key": "P-104",
            "name": "Premium Filter",
            "category": "critical",
            "unit": "unit",
            "standard_cost": _money(20),
        },
        {
            "business_key": "P-105",
            "name": "Growth Kit",
            "category": "growth",
            "unit": "unit",
            "standard_cost": _money(15),
        },
        {
            "business_key": "P-110",
            "name": "Stable Accessory",
            "category": "core",
            "unit": "unit",
            "standard_cost": _money(8),
        },
    ]
    salespeople = [
        {"business_key": "SP-001", "name": "Ana Silva"},
        {"business_key": "SP-002", "name": "Bruno Costa"},
    ]
    suppliers = [
        {"business_key": "SUP-001", "name": "Reliable Supply", "lead_time_days": 7},
        {"business_key": "SUP-002", "name": "Delayed Components", "lead_time_days": 10},
    ]
    cost_centers = [
        {"business_key": "CC-SALES", "name": "Commercial", "area": "sales"},
        {"business_key": "CC-OPS", "name": "Operations", "area": "operations"},
        {
            "business_key": "CC-ADMIN",
            "name": "Administration",
            "area": "administration",
        },
    ]
    rows: dict[str, list[dict[str, Any]]] = {
        "customer": customers,
        "product": products,
        "salesperson": salespeople,
        "supplier": suppliers,
        "cost_center": cost_centers,
        "sales_document": [],
        "sales_document_line": [],
        "inventory_movement": [],
        "stock_balance": [],
        "purchase_order": [],
        "purchase_order_line": [],
        "goods_receipt": [],
        "goods_receipt_line": [],
        "payroll_concept": [],
        "employee_payroll_summary": [],
        "payroll_summary_line": [],
        "accounting_period": [],
        "account_balance": [],
    }
    concepts = [
        {
            "business_key": "PC-FIXED",
            "name": "Fixed compensation",
            "component_type": "fixed",
        },
        {
            "business_key": "PC-VARIABLE",
            "name": "Variable compensation",
            "component_type": "variable",
        },
        {"business_key": "PC-OT", "name": "Overtime", "component_type": "overtime"},
    ]
    rows["payroll_concept"] = concepts

    customer_keys: list[str] = [str(c["business_key"]) for c in customers]
    product_keys: list[str] = [str(p["business_key"]) for p in products]
    sales_qty: dict[str, list[int]] = {
        "P-100": [35, 35, 35, 36],
        "P-104": [28, 28, 8, 30],
        "P-105": [15, 16, 24, 26],
        "P-110": [20, 20, 20, 21],
    }
    prices: dict[str, int] = {"P-100": 30, "P-104": 52, "P-105": 40, "P-110": 22}
    costs: dict[str, list[int]] = {
        "P-100": [12, 12, 12, 12],
        "P-104": [20, 20, 28, 28],
        "P-105": [15, 15, 15, 15],
        "P-110": [8, 8, 8, 8],
    }
    for month_index, (period_start, _) in enumerate(MONTHS):
        for product_key in product_keys:
            quantity = sales_qty[product_key][month_index]
            for offset in range(quantity):
                customer_key = customer_keys[
                    (offset + month_index) % len(customer_keys)
                ]
                document_key = (
                    f"SO-{month_index + 1:02d}-{product_key}-{offset + 1:03d}"
                )
                rows["sales_document"].append(
                    {
                        "business_key": document_key,
                        "document_date": period_start.replace(day=min(offset + 1, 28)),
                        "customer_key": customer_key,
                        "salesperson_key": "SP-001" if offset % 2 == 0 else "SP-002",
                        "currency": CURRENCY,
                        "status": "posted",
                    }
                )
                rows["sales_document_line"].append(
                    {
                        "sales_document_key": document_key,
                        "line_number": 1,
                        "product_key": product_key,
                        "quantity": Decimal("1"),
                        "unit_price": _money(prices[product_key]),
                        "discount": Decimal("0"),
                    }
                )
            rows["inventory_movement"].append(
                {
                    "business_key": f"SALE-{month_index + 1:02d}-{product_key}",
                    "movement_date": period_start,
                    "product_key": product_key,
                    "movement_type": "sale",
                    "quantity": Decimal(-quantity),
                    "reference_key": f"PERIOD-{period_start:%Y-%m}",
                }
            )
            stock = (
                0
                if product_key == "P-104" and month_index == 2
                else (12 if product_key == "P-104" and month_index == 1 else 35)
            )
            rows["stock_balance"].append(
                {
                    "product_key": product_key,
                    "balance_date": period_start,
                    "quantity": Decimal(stock),
                }
            )

        for product_key in product_keys:
            supplier_key = "SUP-002" if product_key == "P-104" else "SUP-001"
            po_key = f"PO-{month_index + 1:02d}-{product_key}"
            delayed = product_key == "P-104" and month_index == 1
            expected = date(2025, 3, 5) if delayed else period_start.replace(day=7)
            status = "partial" if delayed else "received"
            rows["purchase_order"].append(
                {
                    "business_key": po_key,
                    "order_date": period_start,
                    "expected_date": expected,
                    "supplier_key": supplier_key,
                    "status": status,
                    "currency": CURRENCY,
                }
            )
            line_key = f"{po_key}-1"
            rows["purchase_order_line"].append(
                {
                    "business_key": line_key,
                    "purchase_order_key": po_key,
                    "line_number": 1,
                    "product_key": product_key,
                    "ordered_quantity": Decimal(45),
                    "unit_cost": _money(costs[product_key][month_index]),
                }
            )
            if not delayed:
                receipt_key = f"GR-{month_index + 1:02d}-{product_key}"
                rows["goods_receipt"].append(
                    {
                        "business_key": receipt_key,
                        "receipt_date": period_start.replace(day=10),
                        "purchase_order_key": po_key,
                        "status": "received",
                    }
                )
                rows["goods_receipt_line"].append(
                    {
                        "goods_receipt_key": receipt_key,
                        "purchase_order_line_key": line_key,
                        "received_quantity": Decimal(45),
                    }
                )
                rows["inventory_movement"].append(
                    {
                        "business_key": f"RECEIPT-{month_index + 1:02d}-{product_key}",
                        "movement_date": period_start.replace(day=10),
                        "product_key": product_key,
                        "movement_type": "receipt",
                        "quantity": Decimal(45),
                        "reference_key": receipt_key,
                    }
                )
            elif month_index == 1:
                receipt_key = f"GR-02-{product_key}-LATE"
                rows["goods_receipt"].append(
                    {
                        "business_key": receipt_key,
                        "receipt_date": date(2025, 4, 10),
                        "purchase_order_key": po_key,
                        "status": "partial",
                    }
                )
                rows["goods_receipt_line"].append(
                    {
                        "goods_receipt_key": receipt_key,
                        "purchase_order_line_key": line_key,
                        "received_quantity": Decimal(20),
                    }
                )

        fixed = 15000 + month_index * 100
        overtime = 700 if month_index < 3 else 2200
        variable = 1200 + month_index * 50
        for center_index, center_key in enumerate(("CC-SALES", "CC-OPS", "CC-ADMIN")):
            values = {
                "PC-FIXED": fixed // 3,
                "PC-VARIABLE": variable // 3,
                "PC-OT": overtime // 3,
            }
            total = sum(values.values())
            summary_key = f"PAY-{period_start:%Y-%m}-{center_key}"
            rows["employee_payroll_summary"].append(
                {
                    "business_key": summary_key,
                    "period_start": period_start,
                    "period_end": MONTHS[month_index][1],
                    "employee_count": 10 + center_index,
                    "cost_center_key": center_key,
                    "total_cost": _money(total),
                    "currency": CURRENCY,
                }
            )
            for concept_key, amount in values.items():
                rows["payroll_summary_line"].append(
                    {
                        "payroll_summary_key": summary_key,
                        "payroll_concept_key": concept_key,
                        "amount": _money(amount),
                    }
                )

        period_key = f"PERIOD-{period_start:%Y-%m}"
        rows["accounting_period"].append(
            {
                "business_key": period_key,
                "period_start": period_start,
                "period_end": MONTHS[month_index][1],
                "status": "closed",
                "currency": CURRENCY,
            }
        )
        revenue = sum(sales_qty[p][month_index] * prices[p] for p in product_keys)
        cost = sum(
            sales_qty[p][month_index] * costs[p][month_index] for p in product_keys
        )
        payroll = 3 * (fixed // 3 + variable // 3 + overtime // 3)
        rows["account_balance"].extend(
            [
                {
                    "accounting_period_key": period_key,
                    "account_code": "4000",
                    "account_name": "Sales revenue",
                    "account_group": "revenue",
                    "cost_center_key": None,
                    "amount": _money(revenue),
                },
                {
                    "accounting_period_key": period_key,
                    "account_code": "5000",
                    "account_name": "Cost of goods sold",
                    "account_group": "cost",
                    "cost_center_key": "CC-OPS",
                    "amount": _money(-cost),
                },
                {
                    "accounting_period_key": period_key,
                    "account_code": "6100",
                    "account_name": "Payroll expense",
                    "account_group": "expense",
                    "cost_center_key": "CC-OPS",
                    "amount": _money(-payroll),
                },
            ]
        )

    # Add explicit opening/reconciliation adjustments so each snapshot is
    # reproducible from the movement ledger rather than being an unrelated fact.
    for product_key in product_keys:
        for period_start, _ in MONTHS:
            actual = sum(
                (
                    row["quantity"]
                    for row in rows["inventory_movement"]
                    if row["product_key"] == product_key
                    and row["movement_date"] <= period_start
                ),
                Decimal("0"),
            )
            target = next(
                row["quantity"]
                for row in rows["stock_balance"]
                if row["product_key"] == product_key
                and row["balance_date"] == period_start
            )
            adjustment = target - actual
            if adjustment:
                rows["inventory_movement"].append(
                    {
                        "business_key": f"ADJ-{period_start:%Y-%m}-{product_key}",
                        "movement_date": period_start,
                        "product_key": product_key,
                        "movement_type": "adjustment",
                        "quantity": adjustment,
                        "reference_key": f"BALANCE-{period_start:%Y-%m}",
                    }
                )
    return rows
