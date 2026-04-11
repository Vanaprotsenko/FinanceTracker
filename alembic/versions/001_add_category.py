from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '001_add_category'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()

    # Create category table only if it doesn't exist yet
    if 'category' not in existing_tables:
        op.create_table(
            'category',
            sa.Column('id', sa.UUID(), primary_key=True),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id'), nullable=False),
        )

    # Add category_id column to records table only if it doesn't exist yet
    columns = [c['name'] for c in inspector.get_columns('records')]
    if 'category_id' not in columns:
        op.add_column('records', sa.Column('category_id', sa.UUID(), nullable=True))
        op.create_foreign_key(
            'fk_records_category_id',
            'records', 'category',
            ['category_id'], ['id'],
        )


def downgrade() -> None:
    op.drop_constraint('fk_records_category_id', 'records', type_='foreignkey')
    op.drop_column('records', 'category_id')
    op.drop_table('category')
