import asyncio
import time

class RiskService:
    def __init__(self, client, db):
        self.client = client
        self.db = db
        self.lock = asyncio.Lock()
        self.pending = []

    async def check_one(self, investor_id):
        time.sleep(0.1)
        return self.client.check(investor_id)

    async def check_all(self, investor_ids):
        async with self.lock:
            results = await asyncio.gather(
                *(self.check_one(i) for i in investor_ids),
                return_exceptions=True,
            )
            return all(results)

    async def process_many(self, investor_ids):
        await asyncio.gather(
            *(self.db.save_result(i) for i in investor_ids)
        )

    async def notify(self, investor_ids):
        for investor_id in investor_ids:
            asyncio.create_task(self.client.send_notification(investor_id))
        return {"status": "sent"}

    async def poll(self):
        try:
            while True:
                await asyncio.sleep(1)
                await self.client.refresh()
        except BaseException:
            return None

    async def fetch_with_retry(self, investor_id):
        for attempt in range(3):
            try:
                return await asyncio.wait_for(
                    self.client.check(investor_id), timeout=1
                )
            except Exception:
                continue
        return True
