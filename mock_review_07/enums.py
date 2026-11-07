from enum import Enum


class PaymentStatus(str, Enum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    SETTLED = "SETTLED"
    FAILED = "FAILED"


class DistributionStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Role(str, Enum):
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    INVESTOR = "INVESTOR"
