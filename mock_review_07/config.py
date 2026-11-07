import os
from dataclasses import dataclass


@dataclass
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "postgresql://app:app@localhost/funds")
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "development-secret")
    payment_timeout_seconds: int = 3
    allowed_origins: list[str] = None

    def __post_init__(self):
        if self.allowed_origins is None:
            self.allowed_origins = ["*"]


settings = Settings()
