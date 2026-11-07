from collections import defaultdict
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models.entities import Customer

router = APIRouter(prefix="/customers", tags=["portfolio"], dependencies=[Depends(current_user)])


@router.get("/{customer_id}/portfolio")
def portfolio(customer_id: str, db: Session = Depends(get_db)):
    if not db.get(Customer, customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    rows = (
        db.execute(
            text("""
        SELECT account_id, instrument_id, symbol, instrument_name, asset_class, quantity, avg_cost,
               last_price, price_as_of, snapshot_date, market_value, unrealised_pnl
        FROM portfolio_positions_v WHERE customer_id = :customer_id
        ORDER BY account_id, market_value DESC
    """),
            {"customer_id": customer_id},
        )
        .mappings()
        .all()
    )
    allocation = defaultdict(Decimal)
    account_totals = defaultdict(Decimal)
    total = Decimal(0)
    positions = []
    price_dates, snapshot_dates = set(), set()
    for r in rows:
        mv = Decimal(r["market_value"])
        allocation[r["asset_class"]] += mv
        account_totals[r["account_id"]] += mv
        total += mv
        price_dates.add(r["price_as_of"])
        snapshot_dates.add(r["snapshot_date"])
        positions.append(dict(r))
    return {
        "customer_id": customer_id,
        "total_market_value": round(total, 2),
        "account_totals": [{"account_id": k, "market_value": round(v, 2)} for k, v in sorted(account_totals.items())],
        "asset_allocation": [
            {
                "asset_class": k,
                "market_value": round(v, 2),
                "percentage": round(float(v / total * 100), 2) if total else 0,
            }
            for k, v in sorted(allocation.items())
        ],
        "positions": positions,
        "price_as_of": max(price_dates) if price_dates else None,
        "snapshot_date": max(snapshot_dates) if snapshot_dates else None,
    }
