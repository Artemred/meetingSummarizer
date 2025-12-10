from pytest import fixture
from fastapi.testclient import TestClient
from main import app


@fixture
def client():
    with TestClient(app) as client:
        yield client


def test_placeholder_view(client):
    res = client.get("/")
    assert res.status_code == 200
