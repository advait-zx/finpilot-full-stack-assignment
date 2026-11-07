import csv
import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, select

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.entities import Account, Customer, Goal, HoldingSnapshot, Instrument, RiskProfile, User
from app.services.imports import import_transactions_csv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("seed")
DATA_DIR = Path("/data") if Path("/data").exists() else Path(__file__).resolve().parents[3] / "data"


def rows(name):
    with (DATA_DIR / name).open("r", encoding="utf-8-sig", newline="") as f:
        yield from csv.DictReader(f)


def dt(v):
    return datetime.strptime(v, "%Y-%m-%d").date()


def dec(v):
    return Decimal(v)


def seed():
    db = SessionLocal()
    try:
        user_count = db.scalar(select(func.count()).select_from(User)) or 0
        if not user_count:
            db.add_all(
                [
                    User(
                        username=settings.admin_username,
                        password_hash=hash_password(settings.admin_password),
                        role="ADMIN",
                    ),
                    User(
                        username=settings.viewer_username,
                        password_hash=hash_password(settings.viewer_password),
                        role="VIEWER",
                    ),
                ]
            )
            db.commit()
            log.info("Seeded demo users")
        customer_count = db.scalar(select(func.count()).select_from(Customer)) or 0
        if customer_count:
            log.info("Reference data already seeded; skipping CSV bootstrap")
            return
        db.add_all(
            [
                Customer(
                    customer_id=r["customer_id"],
                    full_name=r["full_name"],
                    email=r["email"],
                    phone=r["phone"],
                    city=r["city"],
                    state=r["state"],
                    date_of_birth=dt(r["date_of_birth"]),
                    onboarded_at=dt(r["onboarded_at"]),
                    kyc_status=r["kyc_status"],
                    segment=r["segment"],
                )
                for r in rows("customers.csv")
            ]
        )
        db.flush()
        db.add_all(
            [
                Account(
                    account_id=r["account_id"],
                    customer_id=r["customer_id"],
                    account_type=r["account_type"],
                    provider=r["provider"],
                    opened_at=dt(r["opened_at"]),
                    status=r["status"],
                    base_currency=r["base_currency"],
                )
                for r in rows("accounts.csv")
            ]
        )
        db.flush()  # accounts must exist before holdings/transactions reference them

        db.add_all(
            [
                Instrument(
                    instrument_id=r["instrument_id"],
                    symbol=r["symbol"],
                    instrument_name=r["instrument_name"],
                    asset_class=r["asset_class"],
                    sector=r["sector"],
                    exchange=r["exchange"],
                    currency=r["currency"],
                    last_price=dec(r["last_price"]),
                    price_as_of=dt(r["price_as_of"]),
                    risk_band=r["risk_band"],
                )
                for r in rows("instruments.csv")
            ]
        )
        db.flush()  # instruments must exist before holdings/transactions reference them

        db.add_all(
            [
                Goal(
                    goal_id=r["goal_id"],
                    customer_id=r["customer_id"],
                    goal_type=r["goal_type"],
                    goal_name=r["goal_name"],
                    target_amount=dec(r["target_amount"]),
                    current_funded_amount=dec(r["current_funded_amount"]),
                    target_date=dt(r["target_date"]),
                    priority=r["priority"],
                )
                for r in rows("goals.csv")
            ]
        )
        db.add_all(
            [
                RiskProfile(
                    customer_id=r["customer_id"],
                    risk_score=int(r["risk_score"]),
                    risk_level=r["risk_level"],
                    assessed_at=dt(r["assessed_at"]),
                    horizon_years=int(r["horizon_years"]),
                    liquidity_need=r["liquidity_need"],
                )
                for r in rows("risk_profiles.csv")
            ]
        )
        db.flush()
        seen = set()
        holdings = []
        rejected = 0
        for r in rows("holdings_snapshot.csv"):
            key = (r["account_id"], r["instrument_id"], r["snapshot_date"])
            if key in seen:
                rejected += 1
                continue
            seen.add(key)
            holdings.append(
                HoldingSnapshot(
                    account_id=r["account_id"],
                    instrument_id=r["instrument_id"],
                    quantity=dec(r["quantity"]),
                    avg_cost=dec(r["avg_cost"]),
                    snapshot_date=dt(r["snapshot_date"]),
                )
            )
        db.add_all(holdings)
        db.commit()
        log.info("Seeded reference data; rejected %s duplicate holding rows", rejected)
        raw = (DATA_DIR / "transactions.csv").read_bytes()
        result = import_transactions_csv(db, "transactions.csv", raw)
        log.info(
            "Transaction seed imported=%s rejected=%s batch=%s",
            result["imported_count"],
            result["rejected_count"],
            result["batch_id"],
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed()
