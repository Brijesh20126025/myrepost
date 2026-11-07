from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Fund(Base):
    __tablename__ = "mega_funds"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(150))
    available_cash: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    committed_capital: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)


class Investor(Base):
    __tablename__ = "mega_investors"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, index=True)
    email: Mapped[str] = mapped_column(String(255))


class FundMembership(Base):
    __tablename__ = "mega_fund_memberships"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer)
    fund_id: Mapped[int] = mapped_column(ForeignKey("mega_funds.id"))
    actor_id: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(30))


class CapitalCall(Base):
    __tablename__ = "mega_capital_calls"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, index=True)
    fund_id: Mapped[int] = mapped_column(ForeignKey("mega_funds.id"))
    target_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    collected_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    status: Mapped[str] = mapped_column(String(30), default="OPEN")
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fund = relationship("Fund", lazy="select")


class Payment(Base):
    __tablename__ = "mega_payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, index=True)
    capital_call_id: Mapped[int] = mapped_column(ForeignKey("mega_capital_calls.id"))
    investor_id: Mapped[int] = mapped_column(ForeignKey("mega_investors.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    idempotency_key: Mapped[str] = mapped_column(String(100))
    gateway_reference: Mapped[str | None] = mapped_column(String(150), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="CREATED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    investor = relationship("Investor", lazy="select")
    capital_call = relationship("CapitalCall", lazy="select")


class Distribution(Base):
    __tablename__ = "mega_distributions"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, index=True)
    fund_id: Mapped[int] = mapped_column(ForeignKey("mega_funds.id"))
    investor_id: Mapped[int] = mapped_column(ForeignKey("mega_investors.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    status: Mapped[str] = mapped_column(String(30), default="DRAFT")
    approved_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    investor = relationship("Investor", lazy="select")


class LedgerEntry(Base):
    __tablename__ = "mega_ledger_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer)
    reference_type: Mapped[str] = mapped_column(String(30))
    reference_id: Mapped[int] = mapped_column(Integer)
    account: Mapped[str] = mapped_column(String(50))
    direction: Mapped[str] = mapped_column(String(6))
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))


class OutboxEvent(Base):
    __tablename__ = "mega_outbox"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(100))
    aggregate_id: Mapped[int] = mapped_column(Integer)
    payload: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class WebhookReceipt(Base):
    __tablename__ = "mega_webhook_receipts"
    id: Mapped[int] = mapped_column(primary_key=True)
    gateway_event_id: Mapped[str] = mapped_column(String(120))
    payload: Mapped[str] = mapped_column(Text)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
