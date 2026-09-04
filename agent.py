"""
Local Screen Reader Agent
Reads or explains highlighted screen content aloud using local LLM and free high-quality neural voice.
Zero paid API keys needed.
"""

import time
import sys
import threading
import keyboard
from capture import get_selected_text
from reader import TextToSpeechReader
from llm import LocalLLM


class ScreenReaderAgent:
    def __init__(self, voice="en-US-ChristopherNeural", model="qwen2.5:1.5b"):
        self.reader = TextToSpeechReader(voice=voice)
        self.llm = LocalLLM(model=model)
        self.is_busy = False

    def on_read_selection(self):
        """Reads highlighted text 100% verbatim with zero alterations."""
        if self.is_busy:
            self.reader.stop()

        print("\n[Agent] [F8] Grabbing highlighted text...")
        text = get_selected_text()
        if not text:
            print("[Agent] No text selected. Please highlight text with your mouse and press F8.")
            return

        print(f"[Agent] Exact Text ({len(text)} chars):\n----------------------------------------\n{text}\n----------------------------------------")
        print("[Agent] Reading aloud verbatim...")
        self.reader.speak(text)

    def on_explain_selection(self):
        """Explains highlighted text accurately using local LLM."""
        if self.is_busy:
            self.reader.stop()

        def _worker():
            self.is_busy = True
            try:
                print("\n[Agent] [F9] Grabbing highlighted text for explanation...")
                text = get_selected_text()
                if not text:
                    print("[Agent] No text selected. Highlight text and press F9.")
                    return

                print(f"[Agent] Source Text ({len(text)} chars):\n{text}\n")
                print(f"[Agent] Processing through local LLM ({self.llm.model})...")
                explanation = self.llm.explain_or_summarize(text)
                print(f"\n[Agent] Explanation:\n----------------------------------------\n{explanation}\n----------------------------------------")
                print("[Agent] Reading explanation...")
                self.reader.speak(explanation)
            finally:
                self.is_busy = False
                self.llm.unload()

        threading.Thread(target=_worker, daemon=True).start()

    def on_stop(self):
        """Stops reading immediately."""
        print("\n[Agent] [Stop] Halting playback.")
        self.reader.stop()

    def start(self):
        ollama_status = f"Ready ({self.llm.model}) [Auto-Unload Active]" if self.llm.is_available() else "Offline (Verbatim speech active)"
        
        banner = f"""
===================================================================
       LOCAL SCREEN READER AGENT (ZERO RESIDUAL VRAM)
===================================================================
  Ollama Status : {ollama_status}
  Voice Engine  : Microsoft Neural ({self.reader.voice})
  
  CONTROLS:
    [ F8 ]  or [ Ctrl+Alt+R ] -> READ exact highlighted text (100% Verbatim)
    [ F9 ]  or [ Ctrl+Alt+E ] -> EXPLAIN highlighted text with Local LLM
    [ Esc ] or [ F10 ]        -> STOP / MUTE immediately
    [ Ctrl+C ] in terminal    -> Exit application
===================================================================
Highlight text anywhere (PPTX, PDF, Browser, IDE) and press F8!
"""
        print(banner)

        # Register hotkeys
        keyboard.add_hotkey("F8", self.on_read_selection, suppress=False)
        keyboard.add_hotkey("ctrl+alt+r", self.on_read_selection, suppress=False)
        
        keyboard.add_hotkey("F9", self.on_explain_selection, suppress=False)
        keyboard.add_hotkey("ctrl+alt+e", self.on_explain_selection, suppress=False)
        
        keyboard.add_hotkey("F10", self.on_stop, suppress=False)
        keyboard.add_hotkey("esc", self.on_stop, suppress=False)

        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n[Agent] Shutting down...")
            self.reader.stop()
            self.llm.unload()


if __name__ == "__main__":
    agent = ScreenReaderAgent()
    agent.start()
