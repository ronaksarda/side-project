"""
Local LLM interface for Screen Reader Agent.
Communicates directly with local Ollama instance with zero paid API keys.
Configured with keep_alive=0 to immediately unload models from RAM/VRAM after inference.
"""

import requests
import json
from typing import Optional


class LocalLLM:
    def __init__(self, model: str = "qwen2.5:1.5b", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host.rstrip("/")

    def is_available(self) -> bool:
        """Checks if local Ollama daemon is reachable."""
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=1.5)
            return resp.status_code == 200
        except Exception:
            return False

    def unload(self):
        """Forces Ollama to immediately purge the model from RAM/VRAM."""
        try:
            requests.post(
                f"{self.host}/api/generate",
                json={"model": self.model, "keep_alive": 0},
                timeout=2.0
            )
        except Exception:
            pass

    def explain_or_summarize(self, text: str, custom_prompt: Optional[str] = None) -> str:
        """
        Faithfully and accurately explains or clarifies dense screen text.
        Uses keep_alive=0 so the model is immediately purged from RAM/VRAM after responding.
        """
        if not text or not text.strip():
            return ""

        system_instruction = (
            "You are a precise, highly accurate screen reading assistant. "
            "Explain the provided text clearly in natural spoken English. "
            "Strictly adhere to the facts, key points, and technical terms in the text. "
            "Do not invent facts, do not omit critical details, and do not use markdown symbols (*, #, `)."
        )

        prompt = custom_prompt or (
            f"Here is the text highlighted on screen:\n\n{text}\n\n"
            "Explain this clearly and accurately for the user to listen to:"
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_instruction,
            "stream": False,
            "keep_alive": 0,  # Immediately frees RAM and GPU VRAM after inference
            "options": {
                "temperature": 0.2,
                "num_predict": 300
            }
        }

        try:
            resp = requests.post(f"{self.host}/api/generate", json=payload, timeout=25.0)
            if resp.status_code == 200:
                data = resp.json()
                response_text = data.get("response", "").strip()
                if response_text:
                    return response_text
        except Exception as e:
            print(f"[LocalLLM] Ollama call failed ({e}), using raw text.")

        return text
