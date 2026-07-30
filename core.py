import threading
import time
import json
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener as KeyboardListener, Key





class AutoClickerCore:
    """Gere o estado e a execução dos cliques automáticos."""

    BUTTON_MAP = {"left": Button.left, "right": Button.right, "middle": Button.middle}

    def __init__(self, on_state_change=None):
        self.mouse = Controller()
        self.running = False
        self.on_state_change = on_state_change

        self.interval = 0.1
        self.button = "left"
        self.click_type = "single"

        self._click_thread = None
        self._hotkey_listener = KeyboardListener(on_press=self._on_key_press)
        self._hotkey_listener.start()

        self.configure(**self._load_settings())

    def configure(self, interval=None, button=None, click_type=None):
        """Atualiza os parâmetros de clique. Lança ValueError se inválidos."""
        if interval is not None:
            if interval <= 0:
                raise ValueError("o intervalo tem de ser maior que zero")
            self.interval = interval
        if button is not None:
            if button not in self.BUTTON_MAP:
                raise ValueError(f"botão desconhecido: {button}")
            self.button = button
        if click_type is not None:
            self.click_type = click_type

    def toggle(self):
        self.stop() if self.running else self.start()

    def start(self):
        if self.running:
            return
        self.running = True
        self._click_thread = threading.Thread(target=self._click_loop, daemon=True)
        self._click_thread.start()
        self._notify()

    def stop(self):
        self.running = False
        self._notify()

    def shutdown(self):
        self.running = False
        self._hotkey_listener.stop()
        self._save_settings()


    def _notify(self):
        if self.on_state_change:
            self.on_state_change(self.running)

    def _on_key_press(self, key):
        if key == Key.f6:
            self.toggle()

    def _click_loop(self):
        button = self.BUTTON_MAP.get(self.button, Button.left)
        count = 2 if self.click_type == "double" else 1

        while self.running:
            self.mouse.click(button, count)
            time.sleep(self.interval)

    def _load_settings(self):
        try:
            with open("settings.json", "r") as s:
                return json.load(s)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"interval": 0.1, "button": "left", "click_type": "single"}

    def _save_settings(self):
        with open("settings.json", "w") as s:
            s.write(f'{{"interval": {self.interval}, "button": "{self.button}", "click_type": "{self.click_type}"}}')