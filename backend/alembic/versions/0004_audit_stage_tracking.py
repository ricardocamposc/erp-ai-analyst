"""Add stage and error tracking to dynamic-query audit."""

from collections.abc import Sequence

from alembic import op

revision: str = "0004_audit_stage_tracking"
down_revision: str | None = "0003_dynamic_query_audit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE analysis_interaction
            ADD COLUMN IF NOT EXISTS current_stage VARCHAR(60) NOT NULL DEFAULT 'received',
            ADD COLUMN IF NOT EXISTS stage_history JSONB NOT NULL DEFAULT '[]'::jsonb,
            ADD COLUMN IF NOT EXISTS error_type VARCHAR(120),
            ADD COLUMN IF NOT EXISTS error_detail TEXT,
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE analysis_interaction
            DROP COLUMN IF EXISTS updated_at,
            DROP COLUMN IF EXISTS error_detail,
            DROP COLUMN IF EXISTS error_type,
            DROP COLUMN IF EXISTS stage_history,
            DROP COLUMN IF EXISTS current_stage;
        """
    )
