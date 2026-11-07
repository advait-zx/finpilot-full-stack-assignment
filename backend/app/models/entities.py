from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    __table_args__ = (CheckConstraint("role IN ('VIEWER','ADMIN')", name="ck_users_role"),)

class Customer(Base):
    __tablename__ = "customers"
    customer_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(20), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    onboarded_at: Mapped[date] = mapped_column(Date, nullable=False)
    kyc_status: Mapped[str] = mapped_column(String(20), nullable=False)
    segment: Mapped[str] = mapped_column(String(20), nullable=False)
    accounts = relationship("Account", back_populates="customer")
    goals = relationship("Goal", back_populates="customer")
    risk_profiles = relationship("RiskProfile", back_populates="customer")
    __table_args__ = (
        CheckConstraint("kyc_status IN ('PENDING','REVIEW','VERIFIED')", name="ck_customers_kyc"),
        CheckConstraint("segment IN ('Mass','Affluent','HNI')", name="ck_customers_segment"),
    )

class Account(Base):
    __tablename__ = "accounts"
    account_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.customer_id", ondelete="RESTRICT"), nullable=False, index=True)
    account_type: Mapped[str] = mapped_column(String(30), nullable=False)
    provider: Mapped[str] = mapped_column(String(150), nullable=False)
    opened_at: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    customer = relationship("Customer", back_populates="accounts")
    __table_args__ = (
        CheckConstraint("account_type IN ('BROKERAGE','MUTUAL_FUND','RETIREMENT')", name="ck_accounts_type"),
        CheckConstraint("status IN ('ACTIVE','CLOSED','DORMANT')", name="ck_accounts_status"),
    )

class Instrument(Base):
    __tablename__ = "instruments"
    instrument_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    instrument_name: Mapped[str] = mapped_column(String(180), nullable=False)
    asset_class: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    sector: Mapped[str] = mapped_column(String(80), nullable=False)
    exchange: Mapped[str] = mapped_column(String(20), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    last_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    price_as_of: Mapped[date] = mapped_column(Date, nullable=False)
    risk_band: Mapped[str] = mapped_column(String(20), nullable=False)

class HoldingSnapshot(Base):
    __tablename__ = "holdings_snapshot"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.account_id", ondelete="RESTRICT"), nullable=False, index=True)
    instrument_id: Mapped[str] = mapped_column(ForeignKey("instruments.instrument_id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    avg_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    __table_args__ = (
        UniqueConstraint("account_id", "instrument_id", "snapshot_date", name="uq_holding_snapshot_position"),
        CheckConstraint("quantity >= 0", name="ck_holdings_quantity"),
        CheckConstraint("avg_cost >= 0", name="ck_holdings_avg_cost"),
        Index("ix_holdings_account_snapshot", "account_id", "snapshot_date"),
    )

class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.account_id", ondelete="RESTRICT"), nullable=False, index=True)
    instrument_id: Mapped[str | None] = mapped_column(ForeignKey("instruments.instrument_id", ondelete="RESTRICT"), nullable=True, index=True)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    __table_args__ = (
        CheckConstraint("transaction_type IN ('BUY','SELL','DIVIDEND','FEE')", name="ck_transactions_type"),
        CheckConstraint("status IN ('PENDING','REVERSED','SETTLED')", name="ck_transactions_status"),
        CheckConstraint("quantity >= 0", name="ck_transactions_quantity"),
        CheckConstraint("price >= 0", name="ck_transactions_price"),
        Index("ix_transactions_account_trade_date", "account_id", "trade_date"),
    )

class Goal(Base):
    __tablename__ = "goals"
    goal_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True)
    goal_type: Mapped[str] = mapped_column(String(30), nullable=False)
    goal_name: Mapped[str] = mapped_column(String(180), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    current_funded_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    customer = relationship("Customer", back_populates="goals")
    __table_args__ = (
        CheckConstraint("target_amount > 0", name="ck_goals_target_positive"),
        CheckConstraint("current_funded_amount >= 0", name="ck_goals_funded_nonnegative"),
        CheckConstraint("priority IN ('LOW','MEDIUM','HIGH')", name="ck_goals_priority"),
    )

class RiskProfile(Base):
    __tablename__ = "risk_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(30), nullable=False)
    assessed_at: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    horizon_years: Mapped[int] = mapped_column(Integer, nullable=False)
    liquidity_need: Mapped[str] = mapped_column(String(20), nullable=False)
    customer = relationship("Customer", back_populates="risk_profiles")
    __table_args__ = (
        UniqueConstraint("customer_id", "assessed_at", name="uq_risk_customer_assessed"),
        CheckConstraint("risk_score BETWEEN 0 AND 100", name="ck_risk_score"),
        CheckConstraint("horizon_years > 0", name="ck_risk_horizon"),
        CheckConstraint("liquidity_need IN ('LOW','MEDIUM','HIGH')", name="ck_risk_liquidity"),
    )

class ImportBatch(Base):
    __tablename__ = "import_batches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    imported_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rejected_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class ImportReject(Base):
    __tablename__ = "import_rejects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("import_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_payload: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
