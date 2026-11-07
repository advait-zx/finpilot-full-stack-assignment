"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-11-06
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    from app.models.base import Base
    from app.models import entities  # noqa: F401
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)
    op.execute("""
        CREATE OR REPLACE VIEW portfolio_positions_v AS
        SELECT h.account_id, a.customer_id, h.instrument_id, i.symbol, i.instrument_name,
               i.asset_class, h.quantity, h.avg_cost, i.last_price, i.price_as_of, h.snapshot_date,
               ROUND((h.quantity * i.last_price)::numeric, 2) AS market_value,
               ROUND((h.quantity * (i.last_price - h.avg_cost))::numeric, 2) AS unrealised_pnl
        FROM holdings_snapshot h
        JOIN accounts a ON a.account_id = h.account_id
        JOIN instruments i ON i.instrument_id = h.instrument_id;
    """)

def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS portfolio_positions_v")
    from app.models.base import Base
    from app.models import entities  # noqa: F401
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
