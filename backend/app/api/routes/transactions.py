from datetime import date
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.db.session import get_db
from app.models.entities import Account, Instrument, Transaction

router = APIRouter(prefix="/customers", tags=["transactions"], dependencies=[Depends(current_user)])

@router.get("/{customer_id}/transactions")
def transactions(customer_id: str, start_date: date | None = None, end_date: date | None = None, account_id: str | None = None, instrument_id: str | None = None, transaction_type: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100), db: Session = Depends(get_db)):
    base = select(Transaction, Instrument.symbol, Instrument.instrument_name).join(Account, Account.account_id == Transaction.account_id).outerjoin(Instrument, Instrument.instrument_id == Transaction.instrument_id).where(Account.customer_id == customer_id)
    count_stmt = select(func.count()).select_from(Transaction).join(Account, Account.account_id == Transaction.account_id).where(Account.customer_id == customer_id)
    filters = []
    if start_date: filters.append(Transaction.trade_date >= start_date)
    if end_date: filters.append(Transaction.trade_date <= end_date)
    if account_id: filters.append(Transaction.account_id == account_id)
    if instrument_id: filters.append(Transaction.instrument_id == instrument_id)
    if transaction_type: filters.append(Transaction.transaction_type == transaction_type.upper())
    if filters:
        base = base.where(*filters); count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    rows = db.execute(base.order_by(Transaction.trade_date.desc(), Transaction.transaction_id.desc()).offset((page-1)*page_size).limit(page_size)).all()
    items=[]
    for tx,symbol,name in rows:
        items.append({"transaction_id":tx.transaction_id,"account_id":tx.account_id,"instrument_id":tx.instrument_id,"symbol":symbol,"instrument_name":name,"transaction_type":tx.transaction_type,"trade_date":tx.trade_date,"quantity":tx.quantity,"price":tx.price,"amount":tx.amount,"status":tx.status})
    return {"items":items,"meta":{"page":page,"page_size":page_size,"total":total,"pages":ceil(total/page_size) if total else 0}}
