# Local Screen Reader Agent

An offline-first, zero-paid-API screen reader and audio assistant that speaks or explains any highlighted text on your screen (in PowerPoint, Word, PDFs, Browsers, IDEs, Discord, etc.) using high-quality neural voices and local LLMs.

---

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Clone and Navigate](#1-clone-and-navigate)
  - [2. Install Dependencies](#2-install-dependencies)
  - [3. Setup Local LLM (Ollama)](#3-setup-local-llm-ollama)
  - [4. Start the Agent](#4-start-the-agent)
- [How It Works & Controls](#how-it-works--controls)
  - [Hotkey Cheatsheet](#hotkey-cheatsheet)
  - [Reading Modes](#reading-modes)
- [Architecture & Data Flow](#architecture--data-flow)
  - [Project Structure](#project-structure)
  - [Data Pipeline](#data-pipeline)
  - [Core Components](#core-components)
- [Testing](#testing)
- [Configuration & Customization](#configuration--customization)
  - [Changing the Voice](#changing-the-voice)
  - [Using a Different Local LLM Model](#using-a-different-local-llm-model)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

When reviewing dense documents, code, or PowerPoint slides, reading long blocks of text can cause severe eye fatigue. **Local Screen Reader Agent** provides an instant, ambient audio reading layer:
1. **Highlight text anywhere** with your mouse.
2. Press **`F8`** to hear a 100% verbatim, natural neural voice readout.
3. Press **`F9`** to have your local LLM (`qwen2.5:1.5b` or any Ollama model) explain/summarize the text before reading.
4. Press **`Esc`** to silence speech immediately.

**100% Free & Private**: No paid API keys (like ElevenLabs or OpenAI) required. Uses Microsoft Edge Neural TTS with offline Windows SAPI fallback and local Ollama inference.

---

## Key Features

- 🎙️ **Natural Neural Voice (Free)**: Powered by Microsoft Edge TTS (`edge-tts`) for ultra-realistic neural speech.
- ⚡ **Offline SAPI Fallback**: Instant fallback to Windows native `SAPI.SpVoice` if internet connectivity is lost.
- 🧠 **Local LLM Intelligence**: Connects to local Ollama (`qwen2.5:1.5b`) for zero-cost, private summaries and explanations of technical text.
- 🎯 **100% Verbatim Accuracy**: Direct Windows UI Automation (`IUIAutomationTextPattern`) extracts exact selected text across PowerPoint, Word, Chrome, Edge, Acrobat, and VS Code with zero keystroke simulation artifacts.
- 🛑 **Instant Stop Hotkey**: Tap `Esc` or `F10` at any time to instantly cut audio playback.
- 🧪 **Fully Tested**: Comprehensive `pytest` test suite covering capture, TTS reader, local LLM, and agent loops.

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ (Tested on Python 3.12.9) |
| **TTS Engine** | `edge-tts` (Microsoft Neural Voices) + Windows `SAPI.SpVoice` COM |
| **Audio Playback** | `pygame.mixer` (Direct low-latency hardware audio streaming) |
| **Selection Capture** | Windows UI Automation (`uiautomation`, `comtypes`) + `pywin32` Clipboard |
| **Local LLM** | Ollama (`qwen2.5:1.5b`, `llama3.1`, `phi3`, etc.) |
| **Hotkeys** | `keyboard` global listener |
| **Test Suite** | `pytest` |

---

## Prerequisites

1. **Operating System**: Windows 10 or Windows 11.
2. **Python**: Python 3.10 or higher.
3. **Ollama (Optional, for F9 Explanations)**:
   - Download and install Ollama from [ollama.com](https://ollama.com).
   - Pull the lightweight model:
     ```powershell
     ollama pull qwen2.5:1.5b
     ```

---

## Getting Started

### 1. Clone and Navigate

```powershell
git clone https://github.com/ronaksarda/side-project.git
cd side-project
```

### 2. Install Dependencies

Install the required Python packages:

```powershell
pip install edge-tts pygame pywin32 uiautomation comtypes keyboard requests pytest
```

### 3. Setup Local LLM (Ollama)

Ensure Ollama is running in the background:

```powershell
# Verify Ollama is reachable and model is installed
ollama list
```

*(Note: If Ollama is not installed or running, direct verbatim reading with `F8` still works 100% normally).*

### 4. Start the Agent

Run the main agent:

```powershell
python agent.py
```

You will see the startup banner:
```
===================================================================
       LOCAL SCREEN READER AGENT (HIGH ACCURACY)
===================================================================
  Ollama Status : Ready (qwen2.5:1.5b)
  Voice Engine  : Microsoft Neural (en-US-ChristopherNeural)
  
  CONTROLS:
    [ F8 ]  or [ Ctrl+Alt+R ] -> READ exact highlighted text (100% Verbatim)
    [ F9 ]  or [ Ctrl+Alt+E ] -> EXPLAIN highlighted text with Local LLM
    [ Esc ] or [ F10 ]        -> STOP / MUTE immediately
    [ Ctrl+C ] in terminal    -> Exit application
===================================================================
Highlight text anywhere (PPTX, PDF, Browser, IDE) and press F8!
```

---

## How It Works & Controls

### Hotkey Cheatsheet  

| Primary Hotkey | Alternative Hotkey | Action | Description |
| :--- | :--- | :--- | :--- |
| **`F8`** | `Ctrl + Alt + R` | **Verbatim Readout** | Speaks highlighted text word-for-word with zero AI alterations. |
| **`F9`** | `Ctrl + Alt + E` | **LLM Explanation** | Sends highlighted text to Ollama for a concise spoken summary/explanation. |
| **`Esc`** | `F10` | **Stop / Mute** | Immediately halts ongoing speech and resets the playback engine. |
| **`Ctrl + C`** | *(in terminal)* | **Exit Agent** | Gracefully shuts down audio threads and exits. |

### Reading Modes

1. **Verbatim Read Mode (`F8`)**:
   - Highlight any sentence, paragraph, bullet point, or code block.
   - Press `F8`.
   - The agent reads the exact text aloud in natural spoken English.

2. **Smart Explain Mode (`F9`)**:
   - Highlight complex math, architecture docs, dense technical slides, or foreign concepts.
   - Press `F9`.
   - Local `qwen2.5:1.5b` parses the content, extracts the core concepts, and reads an easy-to-understand conversational explanation.

---

## Architecture & Data Flow

### Project Structure

```
side-project/
├── agent.py              # Main daemon entry point & global hotkey orchestration
├── capture.py            # Direct Windows UI Automation & clipboard text extractor
├── reader.py             # Dual-engine TTS player (edge-tts + SAPI + pygame.mixer)
├── llm.py                # Local Ollama client with strict grounding prompts
├── tests/                # Automated test suite
│   ├── test_agent.py     # Agent hotkey & state dispatch tests
│   ├── test_capture.py   # UI Automation & clipboard mock tests
│   ├── test_llm.py       # Ollama request/fallback tests
│   └── test_reader.py    # TTS audio playback & SAPI fallback tests
├── README.md             # Complete project documentation
└── .gitignore            # Git ignore rules
```

### Data Pipeline

```
[User Highlights Text on Screen]
               │
               ▼
   [Presses F8 or F9 Hotkey]
               │
               ▼
      [capture.py: get_selected_text()]
      ├── 1. Windows UI Automation (IUIAutomationTextPattern)
      └── 2. Clean Win32 Clipboard (Fallback)
               │
      ┌────────┴────────┐
      │ (F8)            │ (F9)
      ▼                 ▼
[Direct Text]     [llm.py: LocalLLM (qwen2.5:1.5b)]
      │                 │
      │                 ▼
      │           [Spoken Summary]
      └────────┬────────┘
               │
               ▼
      [reader.py: TextToSpeechReader]
      ├── Primary: edge_tts Neural Stream (.mp3) -> pygame.mixer
      └── Fallback: Windows SAPI.SpVoice (COM)
               │
               ▼
     [🔊 Speaker Audio Output]
```

### Core Components

- **`capture.py`**:
  Uses Windows Accessibility APIs (`IUIAutomationTextPattern`) to directly query the selected text ranges of the focused control. This eliminates keypress collision and works in PowerPoint shapes, browser text, and PDF viewers.
- **`reader.py`**:
  Uses `edge-tts` to generate crisp neural audio streams and plays them through `pygame.mixer`. Handles thread lifecycle, cleanup of temporary media, and provides instant cancellation via `stop()`.
- **`llm.py`**:
  Issues low-temperature (`temp=0.2`), strictly grounded prompts to Ollama (`/api/generate`) to avoid hallucinations and retain technical terms.
- **`agent.py`**:
  Manages the background execution loop, hotkey bindings, busy states, and terminal status logging.

---

## Testing

Run the automated test suite with `pytest`:

```powershell
python -m pytest -v
```

Expected output:
```
============================= test session starts =============================
platform win32 -- Python 3.12.9, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\rocky\OneDrive\Documents\side-project
plugins: anyio-4.13.0
collected 13 items

tests/test_agent.py::test_agent_init PASSED                              [  7%]
tests/test_agent.py::test_agent_read_selection_verbatim PASSED           [ 15%]
tests/test_agent.py::test_agent_read_selection_empty PASSED              [ 23%]
tests/test_agent.py::test_agent_stop PASSED                              [ 30%]
tests/test_capture.py::test_get_selected_text_from_uia PASSED            [ 38%]
tests/test_capture.py::test_get_selected_text_from_clipboard PASSED      [ 46%]
tests/test_capture.py::test_get_selected_text_empty PASSED               [ 53%]
tests/test_llm.py::test_llm_init PASSED                                  [ 61%]
tests/test_llm.py::test_explain_text_mock PASSED                         [ 69%]
tests/test_llm.py::test_explain_text_fallback_on_error PASSED            [ 76%]
tests/test_reader.py::test_reader_init PASSED                            [ 84%]
tests/test_reader.py::test_sapi_fallback PASSED                          [ 92%]
tests/test_reader.py::test_stop_speaking PASSED                          [100%]

============================= 13 passed in 1.95s ==============================
```

---

## Configuration & Customization

### Changing the Voice

In `agent.py`, change the `voice` parameter in `ScreenReaderAgent(voice=...)`:

```python
# Available high-quality voices:
# - "en-US-ChristopherNeural" (Default: Clear, natural male)
# - "en-US-GuyNeural" (Deep, broadcast male)
# - "en-US-JennyNeural" (Warm, natural female)
# - "en-US-AriaNeural" (Expressive female)
# - "en-GB-RyanNeural" (British male)
# - "en-GB-SoniaNeural" (British female)

agent = ScreenReaderAgent(voice="en-US-JennyNeural")
```

To list all available voices installed on Edge TTS:
```powershell
edge-tts --list-voices
```

### Using a Different Local LLM Model

If you have other models downloaded in Ollama (e.g., `llama3.1:8b`, `phi3:mini`, `gemma2:9b`), specify it in `agent.py`:

```python
agent = ScreenReaderAgent(model="llama3.1:8b")
```

---

## Troubleshooting

### 1. No audio heard when pressing `F8`
- Ensure your default Windows audio output device is set correctly.
- Check if your terminal prints `[Agent] Exact Text (...)`. If it shows `No text selected`, make sure text is highlighted before pressing `F8`.
- If internet is unavailable, `reader.py` will automatically switch to offline Windows SAPI voice.

### 2. `F9` fails or returns raw text
- Verify Ollama is running: open `http://localhost:11434` in your browser or run `ollama list` in PowerShell.
- Make sure `qwen2.5:1.5b` (or your chosen model) is installed: `ollama pull qwen2.5:1.5b`.

### 3. Hotkeys not triggering in Administrator apps
- If the application you are highlighting text in (e.g., an elevated CMD/PowerShell window or task manager) is running as Administrator, run `python agent.py` in an **Administrator Terminal** so Windows permits global hotkey hooks across elevated windows.

---

## License

This project is licensed under the MIT License.
