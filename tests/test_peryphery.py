from unittest.mock import patch, MagicMock
from whisper import transcribe
from celery.exceptions import Retry
import pytest
from tasks import summarize_transcription


@patch("whisper.requests.post")
def test_transcribe_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"text": "placeholder"}
    mock_post.return_value = mock_response

    with patch("builtins.open", MagicMock()):
        result = transcribe("placeholder.mp3")

    assert result == "placeholder"
    mock_post.assert_called_once()
    assert mock_post.call_args[0][0].endswith("/v1/audio/transcriptions")


@patch("whisper.requests.post")
@patch("whisper.logger")
def test_transcribe_server_error(mock_logger, mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("Internal Server Error")
    mock_post.return_value = mock_response

    with patch("builtins.open", MagicMock()):
        result = transcribe("placeholder.mp3")

    assert result is None
    mock_logger.error.assert_called()


@patch("whisper.requests.post")
def test_transcribe_connection_error(mock_post):
    mock_post.side_effect = Exception("Connection refused")
    with patch("builtins.open", MagicMock()):
        result = transcribe("placeholder.mp3")
    assert result is None


@patch("tasks.requests.post")
def test_summarize_success(mock_post):
    mock_res = MagicMock()
    mock_res.json.return_value = {"done": True, "response": "OK"}
    mock_post.return_value = mock_res
    result = summarize_transcription.run("Long text")
    assert result == "OK"


@patch("tasks.requests.post")
def test_summarize_retry(mock_post):
    mock_res = MagicMock()
    mock_res.json.return_value = {"done": False}
    mock_post.return_value = mock_res

    with patch.object(summarize_transcription, 'retry') as mock_retry:
        mock_retry.side_effect = Retry()
        with pytest.raises(Retry):
            summarize_transcription.run("Some text")
        mock_retry.assert_called_once()


@patch("tasks.requests.post")
def test_summarize_http_error(mock_post):
    mock_post.side_effect = Exception("Network error")
    with pytest.raises(Exception) as excinfo:
        summarize_transcription.run("Some text")
    assert str(excinfo.value) == "Network error"
