from pricing import quote, refund


def test_happy_path():
    assert quote("2") == {"amount": "2.00", "currency": "USD"}
    assert refund("order-7")["status"] == "accepted"
