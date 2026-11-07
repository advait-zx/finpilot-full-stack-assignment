import csv
import io
import json
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Account, ImportBatch, ImportReject, Instrument, Transaction

VALID_TYPES = {"BUY", "SELL", "DIVIDEND", "FEE"}
VALID_STATUS = {"SETTLED", "PENDING", "REVERSED"}
REQUIRED = {
    "transaction_id",
    "account_id",
    "instrument_id",
    "transaction_type",
    "trade_date",
    "quantity",
    "price",
    "amount",
    "status",
}


def validate_transaction_row(
    row: dict, accounts: set[str], instruments: set[str], existing: set[str], seen: set[str], today: date | None = None
) -> dict:
    today = today or date.today()
    txid = row["transaction_id"].strip()
    account = row["account_id"].strip()
    instrument = row["instrument_id"].strip()
    tx_type = row["transaction_type"].strip().upper()
    status = row["status"].strip().upper()
    if not txid:
        raise ValueError("transaction_id is required")
    if txid in existing or txid in seen:
        raise ValueError("duplicate transaction_id")
    if account not in accounts:
        raise ValueError("invalid account_id reference")
    if instrument not in instruments:
        raise ValueError("invalid instrument_id reference")
    if tx_type not in VALID_TYPES:
        raise ValueError("invalid transaction_type")
    if status not in VALID_STATUS:
        raise ValueError("invalid status")
    trade_date = datetime.strptime(row["trade_date"], "%Y-%m-%d").date()
    if trade_date > today:
        raise ValueError("trade_date cannot be in the future")
    quantity = Decimal(row["quantity"])
    price = Decimal(row["price"])
    amount = Decimal(row["amount"])
    if quantity < 0:
        raise ValueError("quantity cannot be negative")
    if price < 0:
        raise ValueError("price cannot be negative")
    if amount < 0:
        raise ValueError("amount cannot be negative")
    return {
        "transaction_id": txid,
        "account_id": account,
        "instrument_id": instrument,
        "transaction_type": tx_type,
        "trade_date": trade_date,
        "quantity": quantity,
        "price": price,
        "amount": amount,
        "status": status,
    }


def _reject(db: Session, batch: ImportBatch, row_number: int, row: dict, reason: str):
    db.add(
        ImportReject(
            batch_id=batch.id,
            row_number=row_number,
            entity_type="transaction",
            raw_payload=json.dumps(row, default=str),
            reason=reason,
        )
    )


def import_transactions_csv(db: Session, file_name: str, raw: bytes) -> dict:
    batch = ImportBatch(file_name=file_name, imported_count=0, rejected_count=0)
    db.add(batch)
    db.flush()
    try:
        text_data = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        _reject(db, batch, 0, {}, "File must be UTF-8 encoded")
        batch.rejected_count = 1
        db.commit()
        return _summary(db, batch)
    reader = csv.DictReader(io.StringIO(text_data))
    if not reader.fieldnames or not REQUIRED.issubset(set(reader.fieldnames)):
        missing = sorted(REQUIRED - set(reader.fieldnames or []))
        _reject(db, batch, 0, {}, f"Missing required columns: {', '.join(missing)}")
        batch.rejected_count = 1
        db.commit()
        return _summary(db, batch)
    accounts = set(db.scalars(select(Account.account_id)).all())
    instruments = set(db.scalars(select(Instrument.instrument_id)).all())
    existing = set(db.scalars(select(Transaction.transaction_id)).all())
    seen = set()
    for row_number, row in enumerate(reader, start=2):
        try:
            cleaned = validate_transaction_row(row, accounts, instruments, existing, seen)
            db.add(Transaction(**cleaned))
            seen.add(cleaned["transaction_id"])
            batch.imported_count += 1
        except (ValueError, InvalidOperation) as exc:
            batch.rejected_count += 1
            _reject(db, batch, row_number, row, str(exc))
    db.commit()
    return _summary(db, batch)


def _summary(db: Session, batch: ImportBatch) -> dict:
    rejects = db.scalars(
        select(ImportReject).where(ImportReject.batch_id == batch.id).order_by(ImportReject.row_number)
    ).all()
    return {
        "batch_id": batch.id,
        "file_name": batch.file_name,
        "imported_count": batch.imported_count,
        "rejected_count": batch.rejected_count,
        "rejections": [
            {"row_number": r.row_number, "reason": r.reason, "raw_payload": json.loads(r.raw_payload)} for r in rejects
        ],
    }
