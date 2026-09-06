"""
Screen and text capture module for Screen Reader Agent.
Grabs highlighted text reliably across any active Windows application.
"""

import time
import ctypes
import pythoncom
import win32clipboard
import win32con
import win32gui
import win32process
import keyboard
import uiautomation as auto


def switch_to_window(hwnd):
    """Brings the target application window to the active foreground."""
    if not hwnd or not win32gui.IsWindow(hwnd):
        return False
    
    fg = win32gui.GetForegroundWindow()
    if fg == hwnd:
        return True

    try:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        fg_thread = win32process.GetWindowThreadProcessId(fg)[0]
        my_thread = win32process.GetWindowThreadProcessId(hwnd)[0]

        ctypes.windll.user32.AttachThreadInput(fg_thread, my_thread, True)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.BringWindowToTop(hwnd)
        ctypes.windll.user32.AttachThreadInput(fg_thread, my_thread, False)
        time.sleep(0.06)
        return True
    except Exception:
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.06)
            return True
        except Exception:
            return False


def get_selection_from_ui_automation(target_hwnd=None) -> str:
    """Directly extracts selected text from UI Automation if available."""
    try:
        pythoncom.CoInitialize()
    except Exception:
        pass

    try:
        focused = auto.GetFocusedControl()
        if focused:
            pattern = focused.GetPattern(auto.PatternId.TextPattern)
            if pattern:
                ranges = pattern.GetSelection()
                if ranges:
                    text = "".join([r.GetText(-1) for r in ranges]).strip()
                    if text:
                        return text
    except Exception:
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
            time.sleep(0.015)
    return text or ""


def get_selected_text(target_hwnd=None) -> str:
    """
    Grabs the highlighted text on screen:
    1. Focuses target application if triggered from widget.
    2. Tries UI Automation direct extraction.
    3. Triggers simulated Ctrl+C via keyboard library.
    4. If new text was copied, returns it.
    5. If not, falls back to current clipboard text so nothing is lost.
    """
    # 1. Focus target window if specified
    if target_hwnd and win32gui.IsWindow(target_hwnd):
        switch_to_window(target_hwnd)

    # 2. Try UI Automation
    uia_text = get_selection_from_ui_automation(target_hwnd=target_hwnd)
    if uia_text and uia_text.strip():
        return uia_text.strip()

    # 3. Record clipboard sequence number
    initial_seq = ctypes.windll.user32.GetClipboardSequenceNumber()
    prev_text = get_clipboard_text()

    # 4. Trigger Ctrl+C
    keyboard.send("ctrl+c")

    # 5. Check if clipboard changed
    for _ in range(12):
        time.sleep(0.02)
        current_seq = ctypes.windll.user32.GetClipboardSequenceNumber()
        if current_seq != initial_seq:
            new_text = get_clipboard_text()
            if new_text and new_text.strip():
                return new_text.strip()

    # 6. If target app didn't change sequence number but updated text
    latest_text = get_clipboard_text()
    if latest_text and latest_text.strip() and latest_text != prev_text:
        return latest_text.strip()

    # 7. Fallback to existing clipboard text if present
    if latest_text and latest_text.strip():
        return latest_text.strip()

    return ""
