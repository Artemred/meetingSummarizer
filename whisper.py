import requests
from config import settings
import logging

logger = logging.getLogger(__name__)

whisper_url = f"http://{settings.WHISPER_HOST}:{settings.WHISPER_PORT}/v1/audio/transcriptions"


def transcribe(file_path: str):
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(whisper_url, files=files)
            response.raise_for_status()
            return response.json()["text"]
    except Exception as e:
        logger.error(f"Error transcribing file {file_path}: {e}")
