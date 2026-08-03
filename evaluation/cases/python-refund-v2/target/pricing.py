from decimal import ROUND_HALF_UP, Decimal


def quote(amount, currency="USD"):
    return {
        "amount": str(Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "currency": currency,
    }


def refund(order_id):
    return {"order_id": order_id, "reason": None, "status": "accepted"}
