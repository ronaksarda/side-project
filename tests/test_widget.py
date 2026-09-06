import pytest
from unittest.mock import MagicMock, patch
from reader import TextToSpeechReader
from widget import FloatingHUD

def test_reader_speed_adjustment():
    reader = TextToSpeechReader()
    assert reader.rate == "+0%"

    reader.set_speed(1.25)
    assert reader.rate == "+25%"

    reader.set_speed(1.5)
    assert reader.rate == "+50%"

    reader.set_speed(2.0)
    assert reader.rate == "+100%"

    reader.set_speed(1.0)
    assert reader.rate == "+0%"

def test_hud_speed_cycle():
    mock_agent = MagicMock()
    mock_agent.reader = TextToSpeechReader()
    
    hud = FloatingHUD(mock_agent)
    hud.speed_btn = MagicMock()
    
    assert hud.speed_levels[hud.speed_idx] == 1.0
    hud._on_speed_click()
    assert hud.speed_levels[hud.speed_idx] == 1.25
    assert mock_agent.reader.rate == "+25%"

def test_hud_stop_click():
    mock_agent = MagicMock()
    hud = FloatingHUD(mock_agent)
    hud._on_stop_click()
    mock_agent.on_stop.assert_called_once()
