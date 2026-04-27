import json
from app.app import app

client = app.test_client()


def test_create_monitor():
    res = client.post("/monitors", json={
        "id": "device-1",
        "timeout": 5,
        "alert_email": "a@b.com"
    })

    assert res.status_code == 201


def test_heartbeat():
    client.post("/monitors", json={
        "id": "device-2",
        "timeout": 5,
        "alert_email": "a@b.com"
    })

    res = client.post("/monitors/device-2/heartbeat")
    assert res.status_code == 200