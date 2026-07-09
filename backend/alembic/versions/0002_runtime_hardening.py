"""harden runtime ids metrics and embedding dimensions

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-09
"""

import sqlalchemy as sa

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Pre-production portfolio migration: old 64-dimensional embeddings cannot be
    # safely resized in place. Drop existing documents/chunks and let demo seeding
    # or document re-upload regenerate 256-dimensional embeddings after upgrade.
    op.execute("DELETE FROM documents")
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(256)")

    op.alter_column("support_tickets", "id", type_=sa.String(64))
    op.add_column("support_tickets", sa.Column("public_id", sa.String(40), nullable=True))
    op.add_column("support_tickets", sa.Column("customer_email", sa.String(255), nullable=True))
    op.execute("UPDATE support_tickets SET public_id = id WHERE public_id IS NULL")
    op.alter_column("support_tickets", "public_id", nullable=False)
    op.create_index("ix_support_tickets_public_id", "support_tickets", ["public_id"], unique=True)

    op.alter_column("handoff_requests", "id", type_=sa.String(64))
    op.add_column("handoff_requests", sa.Column("public_id", sa.String(40), nullable=True))
    op.add_column("handoff_requests", sa.Column("conversation_id", sa.String(64), nullable=True))
    op.execute("UPDATE handoff_requests SET public_id = id WHERE public_id IS NULL")
    op.alter_column("handoff_requests", "public_id", nullable=False)
    op.create_index("ix_handoff_requests_public_id", "handoff_requests", ["public_id"], unique=True)
    op.create_index("ix_handoff_requests_conversation_id", "handoff_requests", ["conversation_id"], unique=False)
    op.create_foreign_key(
        "fk_handoff_requests_conversation_id_conversations",
        "handoff_requests",
        "conversations",
        ["conversation_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("tool_execution_logs", sa.Column("error_code", sa.String(80), nullable=True))
    op.add_column("tool_execution_logs", sa.Column("error_message", sa.Text(), nullable=True))
    op.create_index("ix_tool_execution_logs_error_code", "tool_execution_logs", ["error_code"], unique=False)

    op.create_table(
        "request_metrics",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("conversation_id", sa.String(64), sa.ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("intent", sa.String(80), nullable=False),
        sa.Column("total_ms", sa.Integer(), nullable=False),
        sa.Column("classification_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("retrieval_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("llm_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tool_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("citation_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tool_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_request_metrics_conversation_id", "request_metrics", ["conversation_id"], unique=False)
    op.create_index("ix_request_metrics_intent", "request_metrics", ["intent"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_request_metrics_intent", table_name="request_metrics")
    op.drop_index("ix_request_metrics_conversation_id", table_name="request_metrics")
    op.drop_table("request_metrics")

    op.drop_index("ix_tool_execution_logs_error_code", table_name="tool_execution_logs")
    op.drop_column("tool_execution_logs", "error_message")
    op.drop_column("tool_execution_logs", "error_code")

    op.drop_constraint("fk_handoff_requests_conversation_id_conversations", "handoff_requests", type_="foreignkey")
    op.drop_index("ix_handoff_requests_conversation_id", table_name="handoff_requests")
    op.drop_index("ix_handoff_requests_public_id", table_name="handoff_requests")
    op.drop_column("handoff_requests", "conversation_id")
    op.drop_column("handoff_requests", "public_id")

    op.drop_index("ix_support_tickets_public_id", table_name="support_tickets")
    op.drop_column("support_tickets", "customer_email")
    op.drop_column("support_tickets", "public_id")
    op.alter_column("handoff_requests", "id", type_=sa.String(40))
    op.alter_column("support_tickets", "id", type_=sa.String(40))

    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(64)")
