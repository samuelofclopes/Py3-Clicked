import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from .core import AutoClickerCore

ASSETS = Path(__file__).resolve().parent.parent / "assets"
ICON_PNG = ASSETS / "icon.png"
ICON_ICO = ASSETS / "icon.ico"


class AutoClickerGUI(tk.Tk):
    def __init__(self):
        if sys.platform == "win32":
            import ctypes
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("py3-clicked.app")
            except (AttributeError, OSError):
                pass
        super().__init__()
        self.title("PY3-CLICKED")
        self.resizable(False, False)
        self.geometry("240x260")
        self._set_icon()
        self.core = AutoClickerCore(on_state_change=self._on_core_state_change)

        self.interval_var = tk.StringVar(value=str(self.core.interval))
        self.button_var = tk.StringVar(value=self.core.button)
        self.click_type_var = tk.StringVar(value=self.core.click_type)

        self._build_ui()

        self.interval_var.trace_add("write", self._sync_config)
        self.button_var.trace_add("write", self._sync_config)
        self.click_type_var.trace_add("write", self._sync_config)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _set_icon(self):
        try:
            if sys.platform == "win32":
                self.iconbitmap(default=str(ICON_ICO))  # .ico is the most reliable on Windows
            else:
                self._icon = tk.PhotoImage(file=str(ICON_PNG))  # keep a reference on self!
                self.iconphoto(True, self._icon)
        except tk.TclError:
            pass

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}
        frame = ttk.Frame(self, padding=15)
        frame.grid(row=0, column=0)

        ttk.Label(frame, text="Click interval (s):").grid(
            row=1, column=0, columnspan=2, sticky="w", **pad
        )
        ttk.Entry(frame, textvariable=self.interval_var, width=13).grid(
            row=1, column=1, columnspan=2, sticky="w", **pad
        )

        ttk.Label(frame, text="Mouse button:").grid(row=2, column=0, sticky="w", **pad)
        ttk.Combobox(
            frame, textvariable=self.button_var,
            values=["left", "right", "middle"], state="readonly", width=10
        ).grid(row=2, column=1, sticky="w", **pad)

        ttk.Label(frame, text="Click type:").grid(row=3, column=0, sticky="w", **pad)
        ttk.Combobox(
            frame, textvariable=self.click_type_var,
            values=["single", "double"], state="readonly", width=10
        ).grid(row=3, column=1, sticky="w", **pad)

        ttk.Label(frame, text="Hotkey:").grid(row=4, column=0, sticky="w", **pad)
        self.hotkey_button = ttk.Button(
            frame, width=12, command=self._start_hotkey_capture
        )
        self.hotkey_button.grid(row=4, column=1, sticky="w", **pad)

        self.status_label = ttk.Label(
            frame, text="Status: STOPPED", foreground="red",
            font=("Segoe UI", 11, "bold")
        )
        self.status_label.grid(row=5, column=0, columnspan=2, pady=(15, 5))

        self.toggle_button = ttk.Button(frame, command=self.core.toggle)
        self.toggle_button.grid(row=6, column=0, columnspan=2, pady=(5, 0))

        self.hint_label = ttk.Label(
            frame, font=("Segoe UI", 8), foreground="gray"
        )
        self.hint_label.grid(row=7, column=0, columnspan=2, pady=(10, 0))

        self._refresh_texts()

    def _on_core_state_change(self, running):
        self.after(0, self._update_status, running)

    def _update_status(self, running):
        if running:
            self.status_label.config(text="Status: CLICKING", foreground="green")
            self.toggle_button.config(state="disabled")
            self.after(400, lambda: self.toggle_button.config(state="normal"))
        else:
            self.status_label.config(text="Status: STOPPED", foreground="red")
        self._refresh_texts()

    def _on_close(self):
        self.core.shutdown()
        self.destroy()

    def _key_name(self):
        return self.core.hotkey.upper()  # "f6" -> "F6"

    def _refresh_texts(self):
        key = self._key_name()
        action = "Stop" if self.core.running else "Start"
        self.hotkey_button.config(text=key)
        self.toggle_button.config(text=f"{action} ({key})")
        self.hint_label.config(text=f"Press {key} anywhere to toggle on/off.")

    def _start_hotkey_capture(self):
        self.hotkey_button.config(text="Press a key…")
        self.hint_label.config(text="Press Esc to cancel.")
        self.focus_set()  # take focus off the button so Space doesn't press it again
        # the callback runs on another thread, so it goes through after()
        self.core.capture_hotkey(lambda key: self.after(0, self._refresh_texts))

    def _sync_config(self, *_args):
        # Field by field: an invalid interval (e.g. mid-typing) doesn't
        # stop the button or click type from being applied.
        fields = {
            "interval": lambda: float(self.interval_var.get()),
            "button": self.button_var.get,
            "click_type": self.click_type_var.get,
        }
        for name, getter in fields.items():
            try:
                self.core.configure(**{name: getter()})
            except (tk.TclError, ValueError):
                pass