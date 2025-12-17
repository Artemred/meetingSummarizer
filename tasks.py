from celery_app import celery_app
import os
from whisper import transcribe
import requests
from config import settings
from requests.exceptions import ConnectionError


@celery_app.task(bind=True, max_retries=3)
def transcribe_file(self, path: str):
    try:
        transcription = transcribe(path)
        os.remove(path)
        return transcription
    except ConnectionError as e:
        self.retry(exc=e)
    except FileNotFoundError:
        pass


@celery_app.task(bind=True, max_retries=3)
def summarize_transcription(self, text: str):
    res = requests.post(
        f"http://{settings.SUMMARIZATION_HOST}:{settings.SUMMARIZATION_PORT}/api/generate",
        json={"model": settings.MODEL_NAME, "prompt": text, "stream": False}
    ).json()
    if res.get("done", False):
        return res["response"]
    else:
        self.retry()
