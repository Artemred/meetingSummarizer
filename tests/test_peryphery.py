from unittest.mock import patch, MagicMock
from whisper import transcribe


async def test_whisper():
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status = 200

        mock_response.json = MagicMock(return_value={"text": "transcription result"})
        mock_response.raise_for_status = MagicMock()

        mock_post.return_value = mock_response

        result = transcribe("tests/rec.m4a")
        assert result == "transcription result"
