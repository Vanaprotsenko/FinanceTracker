from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "000_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = set(inspector.get_table_names())

    if "users" not in existing_tables:
        op.create_table(
            "users",
            sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
            sa.Column("email", sa.String(), nullable=False, unique=True),
            sa.Column("name", sa.String(), nullable=True),
            sa.Column("telegram_id", sa.String(), nullable=True, unique=True),
            sa.Column("telegram_username", sa.String(), nullable=True, unique=True),
            sa.Column("password", sa.String(), nullable=False),
            sa.Column("mono_token", sa.String(), nullable=True),
        )

    if "records" not in existing_tables:
        op.create_table(
            "records",
            sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
            sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("amount", sa.Float(), nullable=True),
            sa.Column("type", sa.String(), nullable=True),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column("currency", sa.String(), nullable=True),
            sa.Column("mono_card_id", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )

    if "mono_cards" not in existing_tables:
        op.create_table(
            "mono_cards",
            sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
            sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("card_id", sa.String(), nullable=False, unique=True),
            sa.Column("currency_code", sa.Integer(), nullable=False),
            sa.Column("balance", sa.Float(), nullable=True),
            sa.Column("mono_card_name", sa.String(), nullable=True),
        )

    if "mono_transaction" not in existing_tables:
        op.create_table(
            "mono_transaction",
            sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
            sa.Column("card_id", sa.UUID(), sa.ForeignKey("mono_cards.id", ondelete="CASCADE"), nullable=False),
            sa.Column("time", sa.DateTime(timezone=True), nullable=False),
            sa.Column("description", sa.String(), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("operationAmount", sa.Float(), nullable=False),
            sa.Column("currency", sa.Integer(), nullable=False),
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = set(inspector.get_table_names())

    if "mono_transaction" in existing_tables:
        op.drop_table("mono_transaction")
    if "mono_cards" in existing_tables:
        op.drop_table("mono_cards")
    if "records" in existing_tables:
        op.drop_table("records")
    if "users" in existing_tables:
        op.drop_table("users")
