from fastapi import FastAPI, File, UploadFile, Response
from uuid import uuid4
from config import settings
import aiofiles
from tasks import transcribe_file, summarize_transcription
from celery import chain
from celery.result import AsyncResult
from redis_config import get_redis_connection
import os

os.makedirs(settings.FILE_UPLOAD_DIR, exist_ok=True)

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Placeholder"}


@app.post("/create-session/")
async def create_session(file: UploadFile = File(...)):
    uid = str(uuid4())
    file_path = f"{settings.FILE_UPLOAD_DIR}/{uid}.{file.filename.split(".")[-1]}"
    async with aiofiles.open(file_path, "wb") as f:
        while content := await file.read(1024*1024):
            await f.write(content)
    s1 = transcribe_file.s(file_path).set(task_id="transcribe_"+uid)
    s2 = summarize_transcription.s().set(task_id="summarize_"+uid)
    chain(s1, s2).apply_async()
    redis = await get_redis_connection()
    await redis.set("transcribe_"+uid, "QUEUED")
    await redis.set("summarize_"+uid, "QUEUED")
    return {"id": uid}


@app.get("/session/{uid}")
async def get_session(uid: str, response: Response):
    transcription = AsyncResult("transcribe_"+uid)
    summarize = AsyncResult("summarize_"+uid)
    if transcription.state not in ("QUEUED", "STARTED", "RETRY", "SUCCESS"):
        response.status_code = 404
        return {"error": "session does not exists"}
    return {
        "transcription_status": transcription.state,
        "summary_status": summarize.state,
        "summary": summarize.result
    }
