from pricing import quote, refund


def test_quote_and_refund_contracts():
    assert quote("1.005") == {"amount": "1.00", "currency": "USD"}
    assert refund("order-7", "duplicate")["reason"] == "duplicate"
