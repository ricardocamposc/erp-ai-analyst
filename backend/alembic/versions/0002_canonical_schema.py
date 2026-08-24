"""Create the canonical six-domain analytical schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0002_canonical_schema"
down_revision: str | None = "0001_bootstrap"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE customer (
            id BIGSERIAL PRIMARY KEY, business_key VARCHAR(40) NOT NULL UNIQUE,
            name VARCHAR(120) NOT NULL, segment VARCHAR(40) NOT NULL,
            active BOOLEAN NOT NULL DEFAULT TRUE
        );
        CREATE TABLE product (
            id BIGSERIAL PRIMARY KEY, business_key VARCHAR(40) NOT NULL UNIQUE,
            name VARCHAR(120) NOT NULL, category VARCHAR(60) NOT NULL,
            unit VARCHAR(20) NOT NULL, standard_cost NUMERIC(14,2) NOT NULL CHECK (standard_cost >= 0)
        );
        CREATE TABLE salesperson (
            id BIGSERIAL PRIMARY KEY, business_key VARCHAR(40) NOT NULL UNIQUE,
            name VARCHAR(120) NOT NULL
        );
        CREATE TABLE supplier (
            id BIGSERIAL PRIMARY KEY, business_key VARCHAR(40) NOT NULL UNIQUE,
            name VARCHAR(120) NOT NULL, lead_time_days INTEGER NOT NULL CHECK (lead_time_days >= 0)
        );
        CREATE TABLE cost_center (
            id BIGSERIAL PRIMARY KEY, business_key VARCHAR(40) NOT NULL UNIQUE,
            name VARCHAR(120) NOT NULL, area VARCHAR(60) NOT NULL
        );
        CREATE TABLE sales_document (
            id BIGSERIAL PRIMARY KEY, business_key VARCHAR(40) NOT NULL UNIQUE,
            document_date DATE NOT NULL, customer_id BIGINT NOT NULL REFERENCES customer(id),
            salesperson_id BIGINT NOT NULL REFERENCES salesperson(id), currency CHAR(3) NOT NULL,
            status VARCHAR(20) NOT NULL CHECK (status IN ('posted','cancelled'))
        );
        CREATE TABLE sales_document_line (
            id BIGSERIAL PRIMARY KEY, sales_document_id BIGINT NOT NULL REFERENCES sales_document(id) ON DELETE CASCADE,
            line_number INTEGER NOT NULL, product_id BIGINT NOT NULL REFERENCES product(id),
            quantity NUMERIC(14,3) NOT NULL CHECK (quantity > 0), unit_price NUMERIC(14,2) NOT NULL CHECK (unit_price >= 0),
            discount NUMERIC(5,4) NOT NULL DEFAULT 0 CHECK (discount >= 0 AND discount <= 1),
            UNIQUE (sales_document_id, line_number)
        );
        CREATE TABLE inventory_movement (
            id BIGSERIAL PRIMARY KEY, business_key VARCHAR(40) NOT NULL UNIQUE,
            movement_date DATE NOT NULL, product_id BIGINT NOT NULL REFERENCES product(id),
            movement_type VARCHAR(20) NOT NULL CHECK (movement_type IN ('receipt','sale','adjustment')),
            quantity NUMERIC(14,3) NOT NULL CHECK (quantity <> 0), reference_key VARCHAR(40)
        );
        CREATE TABLE stock_balance (
            id BIGSERIAL PRIMARY KEY, product_id BIGINT NOT NULL REFERENCES product(id),
            balance_date DATE NOT NULL, quantity NUMERIC(14,3) NOT NULL CHECK (quantity >= 0),
            UNIQUE (product_id, balance_date)
        );
        CREATE TABLE purchase_order (
            id BIGSERIAL PRIMARY KEY, business_key VARCHAR(40) NOT NULL UNIQUE,
            order_date DATE NOT NULL, expected_date DATE NOT NULL, supplier_id BIGINT NOT NULL REFERENCES supplier(id),
            status VARCHAR(20) NOT NULL CHECK (status IN ('open','partial','received','cancelled')),
            currency CHAR(3) NOT NULL
        );
        CREATE TABLE purchase_order_line (
            id BIGSERIAL PRIMARY KEY, business_key VARCHAR(40) NOT NULL UNIQUE,
            purchase_order_id BIGINT NOT NULL REFERENCES purchase_order(id) ON DELETE CASCADE,
            line_number INTEGER NOT NULL, product_id BIGINT NOT NULL REFERENCES product(id),
            ordered_quantity NUMERIC(14,3) NOT NULL CHECK (ordered_quantity > 0), unit_cost NUMERIC(14,2) NOT NULL CHECK (unit_cost >= 0),
            UNIQUE (purchase_order_id, line_number)
        );
        CREATE TABLE goods_receipt (
            id BIGSERIAL PRIMARY KEY, business_key VARCHAR(40) NOT NULL UNIQUE,
            receipt_date DATE NOT NULL, purchase_order_id BIGINT NOT NULL REFERENCES purchase_order(id),
            status VARCHAR(20) NOT NULL CHECK (status IN ('received','partial'))
        );
        CREATE TABLE goods_receipt_line (
            id BIGSERIAL PRIMARY KEY, goods_receipt_id BIGINT NOT NULL REFERENCES goods_receipt(id) ON DELETE CASCADE,
            purchase_order_line_id BIGINT NOT NULL REFERENCES purchase_order_line(id),
            received_quantity NUMERIC(14,3) NOT NULL CHECK (received_quantity > 0)
        );
        CREATE TABLE payroll_concept (
            id BIGSERIAL PRIMARY KEY, business_key VARCHAR(40) NOT NULL UNIQUE,
            name VARCHAR(120) NOT NULL, component_type VARCHAR(20) NOT NULL CHECK (component_type IN ('fixed','variable','overtime','other'))
        );
        CREATE TABLE employee_payroll_summary (
            id BIGSERIAL PRIMARY KEY, business_key VARCHAR(40) NOT NULL UNIQUE,
            period_start DATE NOT NULL, period_end DATE NOT NULL, employee_count INTEGER NOT NULL CHECK (employee_count >= 0),
            cost_center_id BIGINT NOT NULL REFERENCES cost_center(id), total_cost NUMERIC(14,2) NOT NULL CHECK (total_cost >= 0),
            currency CHAR(3) NOT NULL, UNIQUE (period_start, period_end, cost_center_id)
        );
        CREATE TABLE payroll_summary_line (
            id BIGSERIAL PRIMARY KEY, payroll_summary_id BIGINT NOT NULL REFERENCES employee_payroll_summary(id) ON DELETE CASCADE,
            payroll_concept_id BIGINT NOT NULL REFERENCES payroll_concept(id), amount NUMERIC(14,2) NOT NULL CHECK (amount >= 0),
            UNIQUE (payroll_summary_id, payroll_concept_id)
        );
        CREATE TABLE accounting_period (
            id BIGSERIAL PRIMARY KEY, business_key VARCHAR(40) NOT NULL UNIQUE,
            period_start DATE NOT NULL, period_end DATE NOT NULL, status VARCHAR(20) NOT NULL CHECK (status = 'closed'),
            currency CHAR(3) NOT NULL, UNIQUE (period_start, period_end)
        );
        CREATE TABLE account_balance (
            id BIGSERIAL PRIMARY KEY, accounting_period_id BIGINT NOT NULL REFERENCES accounting_period(id) ON DELETE CASCADE,
            account_code VARCHAR(30) NOT NULL, account_name VARCHAR(120) NOT NULL,
            account_group VARCHAR(30) NOT NULL CHECK (account_group IN ('revenue','cost','expense','other')),
            cost_center_id BIGINT REFERENCES cost_center(id), amount NUMERIC(14,2) NOT NULL,
            UNIQUE (accounting_period_id, account_code, cost_center_id)
        );
        CREATE INDEX ix_sales_document_date ON sales_document(document_date);
        CREATE INDEX ix_inventory_movement_product_date ON inventory_movement(product_id, movement_date);
        CREATE INDEX ix_purchase_order_expected_date ON purchase_order(expected_date);
        CREATE INDEX ix_account_balance_period ON account_balance(accounting_period_id);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS account_balance, accounting_period, payroll_summary_line,
        employee_payroll_summary, payroll_concept, goods_receipt_line, goods_receipt,
        purchase_order_line, purchase_order, stock_balance, inventory_movement,
        sales_document_line, sales_document, cost_center, supplier, salesperson,
        product, customer CASCADE;
        """
    )
