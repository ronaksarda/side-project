import pytest
from unittest.mock import patch, MagicMock
from llm import LocalLLM

def test_llm_init():
    llm = LocalLLM(model="qwen2.5:1.5b")
    assert llm.model == "qwen2.5:1.5b"
    assert llm.host == "http://localhost:11434"

def test_explain_text_mock():
    llm = LocalLLM()
    with patch("llm.requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"response": "This is a concise explanation of the highlighted technical document."}
        mock_post.return_value = mock_resp

        sample_paragraph = (
            "In computing, a database index is a data structure that improves the speed of data retrieval operations "
            "on a database table at the cost of additional writes and storage space to maintain the index data structure."
        )
        result = llm.explain_or_summarize(sample_paragraph)
        assert "concise explanation" in result
        mock_post.assert_called_once()

def test_explain_text_fallback_on_error():
    llm = LocalLLM()
    with patch("llm.requests.post", side_effect=Exception("Connection refused")):
        sample_paragraph = (
            "In computing, a database index is a data structure that improves the speed of data retrieval operations "
            "on a database table at the cost of additional writes and storage space to maintain the index data structure."
        )
        result = llm.explain_or_summarize(sample_paragraph)
        assert result == sample_paragraph
