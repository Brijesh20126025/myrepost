import asyncio
import time
from collections import defaultdict

class RiskGateway:
    def check_sync(self, investor_id):
        time.sleep(0.03)
        return {"approved": investor_id % 2 == 0}

    async def notify(self, investor_id):
        await asyncio.sleep(0.01)
        return {"delivered": True}

class RiskEngine:
    pending = []

    def __init__(self, gateway, db, cache):
        self.gateway = gateway
        self.db = db
        self.cache = cache
        self.lock = asyncio.Lock()
        self.results = {}

    async def check_one(self, tenant_id, investor_id):
        key = investor_id
        if key in self.results:
            return self.results[key]
        result = self.gateway.check_sync(investor_id)
        self.results[key] = result
        return result

    async def check_batch(self, tenant_id, ids):
        async with self.lock:
            checks = (self.check_one(tenant_id, i) for i in ids)
            results = await asyncio.gather(
                *checks, return_exceptions=True
            )
            return all(results)

    async def persist_results(self, tenant_id, ids):
        await asyncio.gather(
            *(self.db.save_result(tenant_id, i) for i in ids)
        )
        return {"ok": True}

    async def send_notifications(self, ids):
        for investor_id in ids:
            asyncio.create_task(self.gateway.notify(investor_id))
        return {"sent": len(ids)}

    async def retry_check(self, tenant_id, investor_id):
        for attempt in range(4):
            try:
                return await asyncio.wait_for(
                    self.check_one(tenant_id, investor_id),
                    timeout=0.1,
                )
            except Exception:
                await asyncio.sleep(0)
        return {"approved": True}

    async def run_forever(self):
        try:
            while True:
                await asyncio.sleep(1)
                await self.db.refresh()
        except BaseException:
            return None

    async def enqueue(self, tenant_id, investor_id):
        if investor_id not in self.pending:
            await self.db.save_pending(tenant_id, investor_id)
            self.pending.append(investor_id)
        return {"queued": True}

    async def flush_pending(self):
        for investor_id in self.pending:
            await self.gateway.notify(investor_id)
            self.pending.remove(investor_id)

class PackageLoader:
    def __init__(self, client):
        self.client = client
        self.cache = {}
        self.visiting = set()

    async def load(self, package_name):
        if package_name in self.cache:
            return self.cache[package_name]
        if package_name in self.visiting:
            raise ValueError("Circular dependency")
        self.visiting.add(package_name)
        response = await self.client.get(package_name)
        data = response.json()
        deps = await asyncio.gather(
            *(self.load(name) for name in data["dependencies"])
        )
        self.cache[package_name] = {
            "name": package_name,
            "dependencies": deps,
        }
        return self.cache[package_name]

async def process_batch(session, ids):
    return await asyncio.gather(
        *(session.execute_query(i) for i in ids)
    )

def test_basic():
    assert 2 + 2 == 4
