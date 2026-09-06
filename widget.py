"""
Floating HUD / Widget for Screen Reader Agent.
A draggable, always-on-top desktop pill providing instant one-click screen reading controls.
Tracks active application windows outside our process so clicks never lose your selected text.
"""

import os
import tkinter as tk
import threading
import time
import ctypes
import win32gui
import win32con
import win32process


class FloatingHUD:
    def __init__(self, agent):
        self.agent = agent
        self.root = None
        self.speed_levels = [1.0, 1.25, 1.5, 2.0]
        self.speed_idx = 0
        self.speed_btn = None
        self.read_btn = None
        self.explain_btn = None
        self._drag_start_x = 0
        self._drag_start_y = 0
        self.last_target_hwnd = None
        self._my_pid = os.getpid()

    def start(self):
        """Starts the Tkinter UI loop."""
        self.root = tk.Tk()
        self.root.title("Screen Reader HUD")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)  # Frameless sleek pill
        self.root.configure(bg="#18181b")

        # Initial placement: Bottom-right corner above taskbar
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = 330
        height = 42
        x = screen_width - width - 40
        y = screen_height - height - 80
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.update()

        # Dragging bindings
        self.root.bind("<ButtonPress-1>", self._on_drag_start)
        self.root.bind("<B1-Motion>", self._on_drag_motion)

        container = tk.Frame(self.root, bg="#18181b", highlightthickness=1, highlightbackground="#3f3f46")
        container.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Drag handle icon
        handle = tk.Label(container, text="⠿", bg="#18181b", fg="#71717a", font=("Segoe UI", 11), cursor="fleur")
        handle.pack(side=tk.LEFT, padx=(8, 4))
        handle.bind("<ButtonPress-1>", self._on_drag_start)
        handle.bind("<B1-Motion>", self._on_drag_motion)

        btn_font = ("Segoe UI", 9, "bold")

        # Read button
        self.read_btn = tk.Button(
            container, text="📖 Read", font=btn_font,
            bg="#27272a", fg="#fafafa", activebackground="#3f3f46", activeforeground="#ffffff",
            bd=0, padx=8, pady=2, cursor="hand2", command=self._on_read_click
        )
        self.read_btn.pack(side=tk.LEFT, padx=3, pady=5)

        # Explain button
        self.explain_btn = tk.Button(
            container, text="💡 Explain", font=btn_font,
            bg="#27272a", fg="#38bdf8", activebackground="#3f3f46", activeforeground="#38bdf8",
            bd=0, padx=8, pady=2, cursor="hand2", command=self._on_explain_click
        )
        self.explain_btn.pack(side=tk.LEFT, padx=3, pady=5)

        # Stop button
        stop_btn = tk.Button(
            container, text="⏹ Stop", font=btn_font,
            bg="#27272a", fg="#f87171", activebackground="#3f3f46", activeforeground="#f87171",
            bd=0, padx=8, pady=2, cursor="hand2", command=self._on_stop_click
        )
        stop_btn.pack(side=tk.LEFT, padx=3, pady=5)

        # Speed toggle button
        self.speed_btn = tk.Button(
            container, text="1.0x", font=btn_font,
            bg="#27272a", fg="#a1a1aa", activebackground="#3f3f46", activeforeground="#ffffff",
            bd=0, padx=6, pady=2, cursor="hand2", command=self._on_speed_click
        )
        self.speed_btn.pack(side=tk.LEFT, padx=3, pady=5)

        # Close button
        close_btn = tk.Button(
            container, text="✕", font=("Segoe UI", 9),
            bg="#18181b", fg="#71717a", activebackground="#27272a", activeforeground="#ffffff",
            bd=0, padx=6, pady=2, cursor="hand2", command=self.root.destroy
        )
        close_btn.pack(side=tk.RIGHT, padx=(0, 4), pady=5)

        # Track foreground window periodically
        self._track_foreground_window()

        self.root.mainloop()

    def _track_foreground_window(self):
        """
        Continuously records the active document/browser window when user is working.
        Strictly ignores windows belonging to this agent/widget process.
        """
        try:
            fg = win32gui.GetForegroundWindow()
            if fg and win32gui.IsWindow(fg):
                _, pid = win32process.GetWindowThreadProcessId(fg)
                if pid != self._my_pid:
                    self.last_target_hwnd = fg
        except Exception:
            pass
        if self.root:
            self.root.after(100, self._track_foreground_window)

    def _on_drag_start(self, event):
        self._drag_start_x = event.x_root - self.root.winfo_x()
        self._drag_start_y = event.y_root - self.root.winfo_y()

    def _on_drag_motion(self, event):
        new_x = event.x_root - self._drag_start_x
        new_y = event.y_root - self._drag_start_y
        self.root.geometry(f"+{new_x}+{new_y}")

    def _on_read_click(self):
        target = self.last_target_hwnd
        threading.Thread(target=lambda: self.agent.on_read_selection(target_hwnd=target), daemon=True).start()

    def _on_explain_click(self):
        target = self.last_target_hwnd
        threading.Thread(target=lambda: self.agent.on_explain_selection(target_hwnd=target), daemon=True).start()

    def _on_stop_click(self):
        self.agent.on_stop()

    def _on_speed_click(self):
        self.speed_idx = (self.speed_idx + 1) % len(self.speed_levels)
        new_speed = self.speed_levels[self.speed_idx]
        self.agent.reader.set_speed(new_speed)
        self.speed_btn.config(text=f"{new_speed}x")
        print(f"[HUD] Speed updated to {new_speed}x")
