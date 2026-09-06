"""
Local Screen Reader Agent
Reads or explains highlighted screen content aloud using local LLM and free high-quality neural voice.
Zero paid API keys needed.
"""

import time
import sys
import threading
import keyboard
import win32gui
from capture import get_selected_text
from reader import TextToSpeechReader
from llm import LocalLLM
from widget import FloatingHUD


class ScreenReaderAgent:
    def __init__(self, voice="en-US-ChristopherNeural", model="qwen2.5:1.5b"):
        self.reader = TextToSpeechReader(voice=voice)
        self.llm = LocalLLM(model=model)
        self.is_busy = False
        self.hud = None

    def on_read_selection(self, target_hwnd=None):
        """Reads highlighted text 100% verbatim with zero alterations."""
        if self.is_busy:
            self.reader.stop()

        # If triggered from widget, ensure focus is on the target app
        if target_hwnd and win32gui.IsWindow(target_hwnd):
            try:
                win32gui.SetForegroundWindow(target_hwnd)
                time.sleep(0.04)
            except Exception:
                pass

        print("\n[Agent] [Read] Grabbing highlighted text...")
        text = get_selected_text(target_hwnd=target_hwnd)
        if not text:
            print("[Agent] No text selected. Please highlight text with your mouse and trigger Read.")
            return

        print(f"[Agent] Exact Text ({len(text)} chars):\n----------------------------------------\n{text}\n----------------------------------------")
        print("[Agent] Reading aloud verbatim...")
        self.reader.speak(text)

    def on_explain_selection(self, target_hwnd=None):
        """Explains highlighted text accurately using local LLM."""
        if self.is_busy:
            self.reader.stop()

        if target_hwnd and win32gui.IsWindow(target_hwnd):
            try:
                win32gui.SetForegroundWindow(target_hwnd)
                time.sleep(0.04)
            except Exception:
                pass

        def _worker():
            self.is_busy = True
            try:
                print("\n[Agent] [Explain] Grabbing highlighted text for explanation...")
                text = get_selected_text(target_hwnd=target_hwnd)
                if not text:
                    print("[Agent] No text selected. Highlight text and trigger Explain.")
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

    def start(self, enable_hud=True):
        ollama_status = f"Ready ({self.llm.model}) [Auto-Unload Active]" if self.llm.is_available() else "Offline (Verbatim speech active)"
        
        banner = f"""
===================================================================
       LOCAL SCREEN READER AGENT (WITH FLOATING HUD)
===================================================================
  Ollama Status : {ollama_status}
  Voice Engine  : Microsoft Neural ({self.reader.voice})
  
  CONTROLS (Available via Floating Toolbar or Keyboard):
    [ Read ]    / [ F8 ]  / [ Ctrl+Alt+R ] -> READ exact highlighted text (Verbatim)
    [ Explain ] / [ F9 ]  / [ Ctrl+Alt+E ] -> EXPLAIN highlighted text with Local LLM
    [ Stop ]    / [ Esc ] / [ F10 ]        -> STOP / MUTE immediately
    [ Speed ]   (1.0x -> 1.25x -> 1.5x -> 2.0x) on floating widget
    [ Ctrl+C ] in terminal                 -> Exit application
===================================================================
Drag the floating widget anywhere on your screen!
"""
        print(banner)

        # Register global hotkeys
        keyboard.add_hotkey("F8", self.on_read_selection, suppress=False)
        keyboard.add_hotkey("ctrl+alt+r", self.on_read_selection, suppress=False)
        
        keyboard.add_hotkey("F9", self.on_explain_selection, suppress=False)
        keyboard.add_hotkey("ctrl+alt+e", self.on_explain_selection, suppress=False)
        
        keyboard.add_hotkey("F10", self.on_stop, suppress=False)
        keyboard.add_hotkey("esc", self.on_stop, suppress=False)

        if enable_hud:
            self.hud = FloatingHUD(self)
            try:
                self.hud.start()
            except KeyboardInterrupt:
                pass
            finally:
                self.reader.stop()
                self.llm.unload()
        else:
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
