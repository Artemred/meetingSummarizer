from pytest import fixture
from main import app
from httpx import AsyncClient, ASGITransport
from celery_app import celery_app


@fixture
async def client():
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
        yield client


@fixture(scope="session", autouse=True)
def celery_eager_mode():
    original_eager = celery_app.conf.task_always_eager
    original_propagate = celery_app.conf.task_eager_propagates
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        task_store_eager_result=True
    )
    yield
    celery_app.conf.update(
        task_always_eager=original_eager,
        task_eager_propagates=original_propagate
    )


async def test_placeholder_view(client):
    res = await client.get("/")
    assert res.status_code == 200


async def test_tasks_chain(client):
    res = await client.post("/create-session/", files={
        "file": ("report.txt", b"Placeholder", "text/plain")
    })
    assert res.status_code == 200
    uid = res.json()["id"]
    res = await client.get(f"/session/{uid}")
    assert res.status_code == 200
    assert res.json()["transcription_status"] == "SUCCESS"
    assert res.json()["summary_status"] == "SUCCESS"
    assert res.json()["summary"] == "Placeholder summary"

    res = await client.get(f"/session/{uid+"qwe"}")
    assert res.status_code == 404
