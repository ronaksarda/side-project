import pytest
from unittest.mock import patch, MagicMock
from agent import ScreenReaderAgent

def test_agent_init():
    agent = ScreenReaderAgent()
    assert agent.is_busy is False
    assert agent.reader is not None
    assert agent.llm is not None

def test_agent_read_selection_verbatim():
    agent = ScreenReaderAgent()
    with patch("agent.get_selected_text", return_value="Exact highlighted PowerPoint text"):
        with patch.object(agent.reader, "speak") as mock_speak:
            agent.on_read_selection()
            mock_speak.assert_called_once_with("Exact highlighted PowerPoint text")

def test_agent_read_selection_empty():
    agent = ScreenReaderAgent()
    with patch("agent.get_selected_text", return_value=""):
        with patch.object(agent.reader, "speak") as mock_speak:
            agent.on_read_selection()
            mock_speak.assert_not_called()

def test_agent_stop():
    agent = ScreenReaderAgent()
    with patch.object(agent.reader, "stop") as mock_stop:
        agent.on_stop()
        mock_stop.assert_called_once()
