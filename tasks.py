from celery_app import celery_app
import os
from whisper import transcribe


@celery_app.task
def transcribe_file(path: str):
    transcription = transcribe(path)
    os.remove(path)
    return transcription


@celery_app.task
def summarize_transcription(text: str):
    #  summarize with openai
    return "Placeholder summary"
