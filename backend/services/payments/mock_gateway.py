from dataclasses import dataclass
import uuid


@dataclass(frozen=True)
class PaymentResult:
    transaction_id: str
    status: str


class MockPaymentGateway:
    def charge(self, invoice) -> PaymentResult:
        return PaymentResult(transaction_id=f"txn_{uuid.uuid4().hex[:16]}", status="SUCCESS")
