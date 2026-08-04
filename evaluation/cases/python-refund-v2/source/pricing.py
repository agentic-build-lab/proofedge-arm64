from decimal import Decimal


def quote(amount, currency="USD"):
    return {"amount": str(Decimal(amount).quantize(Decimal("0.01"))), "currency": currency}


def refund(order_id, reason=None):
    return {"order_id": order_id, "reason": reason, "status": "accepted"}
