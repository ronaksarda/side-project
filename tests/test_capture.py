import pytest
from unittest.mock import patch
from capture import get_selected_text

def test_get_selected_text_from_uia():
    with patch("capture.get_selection_from_ui_automation", return_value="Selected text from PowerPoint"):
        text = get_selected_text()
        assert text == "Selected text from PowerPoint"

def test_get_selected_text_from_clipboard():
    with patch("capture.get_selection_from_ui_automation", return_value=""):
        with patch("capture.get_clipboard_text", side_effect=["", "Clipboard copied text", "Clipboard copied text"]):
            with patch("capture.clean_win32_copy"):
                text = get_selected_text()
                assert text == "Clipboard copied text"

def test_get_selected_text_empty():
    with patch("capture.get_selection_from_ui_automation", return_value=""):
        with patch("capture.get_clipboard_text", return_value=""):
            with patch("capture.clean_win32_copy"):
                text = get_selected_text()
                assert text == ""
