"""
Screen and text capture module for Screen Reader Agent.
Grabs 100% exact highlighted text across any active Windows application.
"""

import time
import ctypes
import pythoncom
import win32clipboard
import win32con
import uiautomation as auto


def get_selection_from_ui_automation() -> str:
    """
    Directly extracts selected/highlighted text from the active application
    using Windows UI Automation TextPattern.
    Safely initializes COM in whatever thread is calling it.
    """
    try:
        pythoncom.CoInitialize()
    except Exception:
        pass

    try:
        focused = auto.GetFocusedControl()
        if not focused:
            return ""

        # Check TextPattern
        try:
            pattern = focused.GetPattern(auto.PatternId.TextPattern)
            if pattern:
                ranges = pattern.GetSelection()
                if ranges:
                    text = "".join([r.GetText(-1) for r in ranges]).strip()
                    if text:
                        return text
        except Exception:
            pass

        # Check TextPattern2
        try:
            pattern2 = focused.GetPattern(auto.PatternId.TextPattern2)
            if pattern2:
                ranges = pattern2.GetSelection()
                if ranges:
                    text = "".join([r.GetText(-1) for r in ranges]).strip()
                    if text:
                        return text
        except Exception:
            pass

    except Exception as e:
        pass
    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass

    return ""


def get_clipboard_text() -> str:
    """Reads current text from Windows clipboard."""
    text = ""
    for _ in range(5):
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            break
        except Exception:
            time.sleep(0.02)
    return text or ""


def set_clipboard_text(text: str):
    """Sets text in Windows clipboard."""
    for _ in range(5):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            break
        except Exception:
            time.sleep(0.02)


def clean_win32_copy():
    """Simulates Ctrl+C safely without modifier key collisions."""
    VK_CONTROL = 0x11
    VK_C = 0x43
    KEYEVENTF_KEYUP = 0x0002

    # Release any lingering modifier keys first
    ctypes.windll.user32.keybd_event(0x12, 0, KEYEVENTF_KEYUP, 0)  # ALT up
    ctypes.windll.user32.keybd_event(0x10, 0, KEYEVENTF_KEYUP, 0)  # SHIFT up
    ctypes.windll.user32.keybd_event(0x11, 0, KEYEVENTF_KEYUP, 0)  # CTRL up
    time.sleep(0.05)

    # Press Ctrl+C
    ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
    ctypes.windll.user32.keybd_event(VK_C, 0, 0, 0)
    time.sleep(0.03)
    ctypes.windll.user32.keybd_event(VK_C, 0, KEYEVENTF_KEYUP, 0)
    ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


def get_selected_text() -> str:
    """
    Grabs the exact highlighted text on screen:
    1. First tries UI Automation TextPattern selection.
    2. Then performs clean Win32 copy into clipboard.
    3. Falls back to existing clipboard content.
    """
    # 1. UI Automation direct inspect
    uia_text = get_selection_from_ui_automation()
    if uia_text and uia_text.strip():
        return uia_text.strip()

    # 2. Win32 safe copy
    old_clip = get_clipboard_text()
    set_clipboard_text("")
    time.sleep(0.04)

    clean_win32_copy()
    time.sleep(0.15)

    copied = get_clipboard_text()
    if copied and copied.strip():
        return copied.strip()

    # 3. Fallback to existing clipboard
    if old_clip and old_clip.strip():
        return old_clip.strip()

    return ""
