import base64
import json

from fastapi import Header, HTTPException

from .enums import Role


class Principal:
    def __init__(self, actor_id, tenant_id, role, funds=[]):
        self.actor_id = actor_id
        self.tenant_id = tenant_id
        self.role = role
        self.funds = funds


def current_principal(authorization: str = Header(default="")) -> Principal:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ")
    try:
        payload = json.loads(base64.urlsafe_b64decode(token + "==="))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    return Principal(
        actor_id=payload["sub"],
        tenant_id=payload["tenant_id"],
        role=payload.get("role", "ANALYST"),
        funds=payload.get("funds", []),
    )


def can_manage_fund(principal: Principal, fund_id: int) -> bool:
    return principal.role == Role.ADMIN or fund_id in principal.funds


def require_admin(principal: Principal):
    if principal.role not in ("ADMIN", "ANALYST"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
