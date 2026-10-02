import json
import math
import sys
import threading

from pynput.keyboard import Key
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Button, Controller

from .paths import settings_file

DEFAULTS = {"interval": 0.1, "button": "left", "click_type": "single", "hotkey": "f6"}


def key_to_str(key):
    """Convert a pynput key to text: Key.f6 -> 'f6', 'A' -> 'a'."""
    name = getattr(key, "name", None)  # special keys (F6, space, shift...)
    if name:
        return name
    char = getattr(key, "char", None)  # regular keys (letters, digits...)
    return char.lower() if char else None


def valid_hotkey(name):
    return isinstance(name, str) and (name in Key.__members__ or len(name) == 1)


class AutoClickerCore:
    """Manages the state and execution of the automatic clicks."""

    BUTTON_MAP = {"left": Button.left, "right": Button.right, "middle": Button.middle}
    CLICK_TYPES = ("single", "double")

    def __init__(self, on_state_change=None):
        self.mouse = Controller()
        self.running = False
        self.on_state_change = on_state_change

        self.interval = DEFAULTS["interval"]
        self.button = DEFAULTS["button"]
        self.click_type = DEFAULTS["click_type"]
        self.hotkey = DEFAULTS["hotkey"]

        self._capture_callback = None
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._click_thread = None

        # Each value is validated on its own: one bad value doesn't discard the others.
        for key, value in self._load_settings().items():
            try:
                self.configure(**{key: value})
            except ValueError:
                pass

        self._hotkey_listener = KeyboardListener(on_press=self._on_key_press)
        self._hotkey_listener.start()

    # ---------- configuration ----------

    def configure(self, interval=None, button=None, click_type=None, hotkey=None):
        """Update the click settings. Raises ValueError if invalid."""
        if interval is not None:
            if (
                isinstance(interval, bool)
                or not isinstance(interval, (int, float))
                or not math.isfinite(interval)
                or interval <= 0
            ):
                raise ValueError("interval must be a number greater than zero")
            self.interval = float(interval)
        if button is not None:
            if button not in self.BUTTON_MAP:
                raise ValueError(f"unknown button: {button}")
            self.button = button
        if click_type is not None:
            if click_type not in self.CLICK_TYPES:
                raise ValueError(f"unknown click type: {click_type}")
            self.click_type = click_type
        if hotkey is not None:
            if not valid_hotkey(hotkey):
                raise ValueError(f"invalid key: {hotkey!r}")
            self.hotkey = hotkey

    def capture_hotkey(self, callback):
        """The next key pressed becomes the hotkey (Esc cancels).

        callback(key_name) is called when done, or callback(None) if it was
        cancelled. It runs on the listener thread, not on the tkinter thread.
        """
        with self._lock:
            self._capture_callback = callback

    # ---------- control ----------

    def toggle(self):
        with self._lock:
            self.stop() if self.running else self.start()

    def start(self):
        with self._lock:
            if self.running:
                return
            self.running = True
            # One Event per thread: stopping and restarting quickly never
            # leaves two threads clicking at the same time.
            stop_event = threading.Event()
            self._stop_event = stop_event
            self._click_thread = threading.Thread(
                target=self._click_loop, args=(stop_event,), daemon=True
            )
            self._click_thread.start()
        self._notify()

    def stop(self):
        with self._lock:
            if not self.running:
                return
            self.running = False
            self._stop_event.set()
        self._notify()

    def shutdown(self):
        self.stop()
        self._hotkey_listener.stop()
        self._save_settings()

    # ---------- internals ----------

    def _notify(self):
        if self.on_state_change:
            self.on_state_change(self.running)

    def _on_key_press(self, key):
        name = key_to_str(key)
        if name is None:
            return

        with self._lock:
            callback, self._capture_callback = self._capture_callback, None
        if callback is not None:  # capture mode: this key does not toggle the clicker
            try:
                if name == "esc":
                    raise ValueError
                self.configure(hotkey=name)
            except ValueError:
                callback(None)
            else:
                callback(name)
            return

        if name == self.hotkey:
            self.toggle()

    def _click_loop(self, stop_event):
        try:
            while not stop_event.is_set():
                button = self.BUTTON_MAP[self.button]
                count = 2 if self.click_type == "double" else 1
                self.mouse.click(button, count)
                stop_event.wait(self.interval)  # wakes up immediately on stop
        except Exception as exc:  # e.g. Wayland without permissions
            print(f"Click error: {exc}", file=sys.stderr)
            self.stop()

    def _load_settings(self):
        try:
            data = json.loads(settings_file().read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        if not isinstance(data, dict):
            return {}
        return {key: data[key] for key in DEFAULTS if key in data}

    def _save_settings(self):
        path = settings_file()
        data = {
            "interval": self.interval,
            "button": self.button,
            "click_type": self.click_type,
            "hotkey": self.hotkey,
        }
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
            tmp.replace(path)  # atomic write
        except OSError as exc:
            print(f"Could not save settings: {exc}", file=sys.stderr)