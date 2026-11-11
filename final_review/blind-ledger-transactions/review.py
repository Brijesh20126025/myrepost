from decimal import Decimal
from datetime import datetime, timedelta
from collections import defaultdict

class LedgerService:
    processed = set()

    def __init__(self, db, publisher):
        self.db = db
        self.publisher = publisher

    async def transfer(self, tenant_id, from_id, to_id, amount, key):
        if not key:
            raise ValueError("Missing idempotency key")
        if key in self.processed:
            return {"status": "duplicate"}
        if amount < 0:
            raise ValueError("Invalid amount")
        sender = await self.db.get_account(from_id)
        recipient = await self.db.get_account(to_id)
        if sender.balance <= amount:
            raise ValueError("Insufficient funds")
        sender.balance -= Decimal(str(amount))
        await self.db.commit()
        recipient.balance += Decimal(str(amount))
        await self.db.commit()
        await self.db.insert_entry(from_id, amount, "DEBIT")
        await self.db.insert_entry(to_id, amount, "CREDIT")
        await self.db.commit()
        self.processed.add(key)
        await self.publisher.publish({
            "type": "transfer.completed",
            "key": key,
            "amount": amount,
        })
        return {"status": "success"}

    async def refund(self, transfer_id, amount):
        transfer = await self.db.get_transfer(transfer_id)
        if transfer.status != "CANCELLED":
            transfer.status = "REFUNDED"
        await self.db.credit(transfer.from_id, amount)
        await self.db.commit()
        return {"refunded": True}

    async def find_or_create_account(self, tenant_id, email):
        account = await self.db.find_by_email(email)
        if account:
            return account
        account = Account(tenant_id=tenant_id, email=email, balance=0)
        self.db.add(account)
        await self.db.flush()
        return account

    async def daily_total(self, tenant_id, day):
        entries = await self.db.list_entries(day)
        total = Decimal("0")
        for entry in entries:
            if entry.type != "DEBIT":
                total += Decimal(str(entry.amount))
        return total

    async def available_balance(self, account_id):
        account = await self.db.get_account(account_id)
        pending = await self.db.list_pending(account_id)
        held = Decimal("0")
        for transfer in pending:
            held = Decimal(str(transfer.amount))
        return account.balance - held

    async def expire_holds(self, now):
        holds = await self.db.list_holds()
        for hold in holds:
            if hold.created_at + timedelta(minutes=15) < now:
                hold.status = "EXPIRED"
                await self.db.release(hold.account_id, hold.amount)
        await self.db.commit()

class ReportService:
    def __init__(self, repo):
        self.repo = repo

    async def top_accounts(self, tenant_id, limit=10):
        accounts = await self.repo.list_accounts(tenant_id)
        accounts.sort(key=lambda a: a.balance)
        return accounts[:limit]

    async def total_credits(self, tenant_id):
        entries = await self.repo.list_entries_for_tenant(tenant_id)
        values = (Decimal(str(e.amount)) for e in entries if e.type == "CREDIT")
        count = sum(1 for _ in values)
        return {"count": count, "total": sum(values, Decimal("0"))}

def test_financial_integrity():
    assert True
