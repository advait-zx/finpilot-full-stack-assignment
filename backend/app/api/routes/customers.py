from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models.entities import Account, Customer, RiskProfile

router = APIRouter(prefix="/customers", tags=["customers"], dependencies=[Depends(current_user)])


@router.get("")
def list_customers(
    q: str | None = None,
    city: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(Customer)
    count_stmt = select(func.count()).select_from(Customer)
    filters = []
    if q:
        pattern = f"%{q.strip()}%"
        filters.append(
            or_(
                Customer.customer_id.ilike(pattern),
                Customer.full_name.ilike(pattern),
                Customer.email.ilike(pattern),
                Customer.city.ilike(pattern),
            )
        )
    if city:
        filters.append(Customer.city.ilike(f"%{city.strip()}%"))
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    rows = db.scalars(stmt.order_by(Customer.customer_id).offset((page - 1) * page_size).limit(page_size)).all()
    return {
        "items": [
            {
                "customer_id": x.customer_id,
                "full_name": x.full_name,
                "email": x.email,
                "city": x.city,
                "state": x.state,
                "kyc_status": x.kyc_status,
                "segment": x.segment,
            }
            for x in rows
        ],
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": ceil(total / page_size) if total else 0,
        },
    }


@router.get("/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    risk = db.scalar(
        select(RiskProfile)
        .where(RiskProfile.customer_id == customer_id)
        .order_by(RiskProfile.assessed_at.desc())
        .limit(1)
    )
    accounts = db.scalars(select(Account).where(Account.customer_id == customer_id).order_by(Account.account_id)).all()
    return {
        "customer": {
            "customer_id": customer.customer_id,
            "full_name": customer.full_name,
            "email": customer.email,
            "phone": customer.phone,
            "city": customer.city,
            "state": customer.state,
            "date_of_birth": customer.date_of_birth,
            "onboarded_at": customer.onboarded_at,
            "kyc_status": customer.kyc_status,
            "segment": customer.segment,
        },
        "latest_risk_profile": None
        if not risk
        else {
            "risk_score": risk.risk_score,
            "risk_level": risk.risk_level,
            "assessed_at": risk.assessed_at,
            "horizon_years": risk.horizon_years,
            "liquidity_need": risk.liquidity_need,
        },
        "accounts": [
            {
                "account_id": a.account_id,
                "account_type": a.account_type,
                "provider": a.provider,
                "opened_at": a.opened_at,
                "status": a.status,
                "base_currency": a.base_currency,
            }
            for a in accounts
        ],
    }
