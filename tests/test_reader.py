import pytest
from unittest.mock import patch, MagicMock
from reader import TextToSpeechReader

def test_reader_init():
    reader = TextToSpeechReader(voice="en-US-GuyNeural")
    assert reader.voice == "en-US-GuyNeural"
    assert reader.is_speaking is False

def test_sapi_fallback():
    reader = TextToSpeechReader()
    with patch("reader.win32com.client.Dispatch") as mock_dispatch:
        mock_voice = MagicMock()
        mock_dispatch.return_value = mock_voice
        reader.speak_sapi("Test speech")
        mock_voice.Speak.assert_called_once_with("Test speech", 1)

def test_stop_speaking():
    reader = TextToSpeechReader()
    reader.is_speaking = True
    reader.stop()
    assert reader.is_speaking is False
