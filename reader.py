"""
Audio reader engine for Screen Reader Agent.
Uses Microsoft Edge TTS (natural neural voices) via pygame.mixer with instant offline Windows SAPI fallback.
"""

import asyncio
import os
import tempfile
import threading
import time
import edge_tts
import win32com.client
import pygame


class TextToSpeechReader:
    def __init__(self, voice="en-US-ChristopherNeural", rate="+0%", volume="+0%"):
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.is_speaking = False
        self._stop_event = threading.Event()
        self._current_thread = None
        self._sapi = None
        self._mixer_initialized = False

    def _ensure_mixer(self):
        if not self._mixer_initialized:
            try:
                pygame.mixer.init()
                self._mixer_initialized = True
            except Exception as e:
                print(f"[Reader] Pygame mixer init warning: {e}")

    def _get_sapi(self):
        # ponytail: SAPI is Windows built-in, zero external dependencies and 100% offline
        if self._sapi is None:
            self._sapi = win32com.client.Dispatch("SAPI.SpVoice")
        return self._sapi

    def speak_sapi(self, text: str):
        """Offline native Windows SAPI speech."""
        sapi = self._get_sapi()
        # 1 = SVSFlagsAsync
        sapi.Speak(text, 1)

    async def _generate_edge_audio(self, text: str, output_path: str):
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate,
            volume=self.volume,
        )
        await communicate.save(output_path)

    def _play_audio_file(self, file_path: str):
        """Plays MP3 audio file using pygame.mixer."""
        self._ensure_mixer()
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy() and not self._stop_event.is_set():
                time.sleep(0.05)

            if self._stop_event.is_set():
                pygame.mixer.music.stop()

            pygame.mixer.music.unload()
        except Exception as e:
            print(f"[Reader] Audio playback error: {e}")
        finally:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass

    def _speak_worker(self, text: str, prefer_edge: bool = True):
        self.is_speaking = True
        self._stop_event.clear()

        temp_audio_file = None
        if prefer_edge:
            try:
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    temp_audio_file = f.name
                
                asyncio.run(self._generate_edge_audio(text, temp_audio_file))
                
                if not self._stop_event.is_set():
                    self._play_audio_file(temp_audio_file)
                self.is_speaking = False
                return
            except Exception as e:
                print(f"[Reader] Edge TTS failed, falling back to SAPI: {e}")
                if temp_audio_file and os.path.exists(temp_audio_file):
                    try:
                        os.remove(temp_audio_file)
                    except Exception:
                        pass

        # Fallback to SAPI
        try:
            import pythoncom
            pythoncom.CoInitialize()
            sapi = win32com.client.Dispatch("SAPI.SpVoice")
            sapi.Speak(text, 0)
            pythoncom.CoUninitialize()
        except Exception as e:
            print(f"[Reader] SAPI failed: {e}")
        finally:
            self.is_speaking = False

    def speak(self, text: str, prefer_edge: bool = True):
        """Starts speaking text in a background thread."""
        if not text or not text.strip():
            return

        self.stop()
        self._current_thread = threading.Thread(
            target=self._speak_worker,
            args=(text, prefer_edge),
            daemon=True
        )
        self._current_thread.start()

    def stop(self):
        """Stops any currently playing audio immediately."""
        self._stop_event.set()
        self.is_speaking = False
        try:
            if self._mixer_initialized and pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass
        if self._sapi:
            try:
                # 2 = SVSFPurgeBeforeSpeak
                self._sapi.Speak("", 2)
            except Exception:
                pass
