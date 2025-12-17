from pytest import fixture, mark
from main import app
from httpx import AsyncClient, ASGITransport
from celery_app import celery_app
from unittest.mock import patch, MagicMock, AsyncMock


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


@mark.asyncio
async def test_tasks_chain(client):
    with patch("main.transcribe_file") as mock_transcribe, \
         patch("main.summarize_transcription") as mock_summarize, \
         patch("main.chain") as mock_chain, \
         patch("main.AsyncResult") as mock_async_result, \
         patch("main.get_redis_connection") as mock_get_redis:

        mock_sig = MagicMock()
        mock_transcribe.s.return_value = mock_sig
        mock_summarize.s.return_value = mock_sig
        mock_chain.return_value.apply_async.return_value = MagicMock()
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        def side_effect(task_id):
            m = MagicMock()
            if "transcribe" in task_id:
                m.state = "SUCCESS"
            elif "summarize" in task_id:
                m.state = "SUCCESS"
                m.result = "Placeholder summary"
            else:
                m.state = "PENDING"
            return m
        mock_async_result.side_effect = side_effect

        res = await client.post("/create-session/", files={
            "file": ("report.txt", b"Placeholder content", "text/plain")
        })

        assert res.status_code == 200
        uid = res.json()["id"]

        res = await client.get(f"/session/{uid}")
        assert res.status_code == 200
        data = res.json()
        assert data["transcription_status"] == "SUCCESS"
        assert data["summary_status"] == "SUCCESS"
        assert data["summary"] == "Placeholder summary"

        mock_async_result.side_effect = None
        mock_async_result.return_value.state = "PENDING"
        res = await client.get(f"/session/{uid + 'qwe'}")
        assert res.status_code == 404
