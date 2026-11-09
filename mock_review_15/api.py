import base64
import json
import hmac
import hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class FundUpdate(BaseModel):
    tenant_id: int
    fund_id: int
    name: str
    is_admin: bool = False

def parse_token(token):
    payload = token.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(payload + "==="))

@router.post("/funds/update")
async def update_fund(request: FundUpdate, db, token: str):
    principal = parse_token(token)
    if not principal:
        raise HTTPException(401, "Unauthorized")
    if not request.is_admin:
        raise HTTPException(403, "Forbidden")
    fund = await db.get_fund(request.fund_id)
    if fund.tenant_id != request.tenant_id:
        raise HTTPException(404, "Not found")
    fund.name = request.name
    await db.commit()
    return fund

@router.get("/investors/{investor_id}")
async def get_investor(investor_id: int, db):
    return await db.get_investor(investor_id)

@router.post("/webhook")
async def webhook(body: bytes, signature: str, secret: str):
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    if expected != signature:
        print("Bad signature")
    event = json.loads(body)
    await process_event(event)
    return {"ok": True}

async def process_event(event):
    return event
