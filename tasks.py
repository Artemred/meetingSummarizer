from celery_app import celery_app
import os


@celery_app.task
def transcribe_file(path: str):
    #  run whisper
    transcription = "Placeholder text"
    os.remove(path)
    return transcription


@celery_app.task
def summarize_transcription(text: str):
    #  summarize with openai
    return "Placeholder summary"
