"""Add auditable dynamic-query interaction records."""

from collections.abc import Sequence

from alembic import op

revision: str = "0003_dynamic_query_audit"
down_revision: str | None = "0002_canonical_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE analysis_interaction (
            id BIGSERIAL PRIMARY KEY,
            request_id VARCHAR(80) NOT NULL,
            conversation_id VARCHAR(80),
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            question TEXT NOT NULL,
            status VARCHAR(30) NOT NULL,
            analysis_goal TEXT,
            sql_candidate TEXT,
            sql_hash VARCHAR(128),
            validation JSONB NOT NULL DEFAULT '{}'::jsonb,
            result JSONB NOT NULL DEFAULT '{}'::jsonb,
            response JSONB NOT NULL DEFAULT '{}'::jsonb,
            warnings JSONB NOT NULL DEFAULT '[]'::jsonb,
            latency_ms INTEGER,
            model_name VARCHAR(120),
            catalog_version VARCHAR(120)
        );
        CREATE INDEX ix_analysis_interaction_created_at
            ON analysis_interaction (created_at);
        CREATE INDEX ix_analysis_interaction_status
            ON analysis_interaction (status);
        CREATE INDEX ix_analysis_interaction_request_id
            ON analysis_interaction (request_id);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS analysis_interaction;")
