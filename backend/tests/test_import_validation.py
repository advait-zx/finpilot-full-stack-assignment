from datetime import date
import pytest
from app.services.imports import validate_transaction_row

BASE={"transaction_id":"T1","account_id":"A1","instrument_id":"I1","transaction_type":"BUY","trade_date":"2026-09-15","quantity":"10","price":"100","amount":"1000","status":"SETTLED"}

def validate(**changes):
    row=BASE|changes
    return validate_transaction_row(row,{"A1"},{"I1"},set(),set(),today=date(2026,11,6))

def test_valid_transaction_row():
    assert validate()["transaction_id"] == "T1"

def test_invalid_instrument_is_rejected():
    with pytest.raises(ValueError,match="invalid instrument_id"):
        validate(instrument_id="I9999")

def test_future_trade_date_is_rejected():
    with pytest.raises(ValueError,match="future"):
        validate(trade_date="2027-01-05")

def test_negative_amount_is_rejected():
    with pytest.raises(ValueError,match="amount cannot be negative"):
        validate(transaction_type="FEE",amount="-75")

def test_duplicate_transaction_is_rejected():
    with pytest.raises(ValueError,match="duplicate"):
        validate_transaction_row(BASE,{"A1"},{"I1"},{"T1"},set(),today=date(2026,11,6))
