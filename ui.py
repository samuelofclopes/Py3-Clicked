import tkinter as tk
from tkinter import ttk

from core import AutoClickerCore


class AutoClickerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PY3-CLICKED")
        self.resizable(False, False)

        self.core = AutoClickerCore(on_state_change=self._on_core_state_change)

        self.interval_var = tk.StringVar(value=str(self.core.interval))
        self.button_var = tk.StringVar(value=self.core.button)
        self.click_type_var = tk.StringVar(value=self.core.click_type)

        self._build_ui()

        self.interval_var.trace_add("write", self._sync_config)
        self.button_var.trace_add("write", self._sync_config)
        self.click_type_var.trace_add("write", self._sync_config)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}
        frame = ttk.Frame(self, padding=15)
        frame.grid(row=0, column=0)

        ttk.Label(frame, text="Intervalo entre cliques (segundos):").grid(
            row=0, column=0, columnspan=2, sticky="w", **pad
        )
        ttk.Entry(frame, textvariable=self.interval_var, width=10).grid(
            row=1, column=0, columnspan=2, sticky="w", **pad
        )

        ttk.Label(frame, text="Botão do rato:").grid(row=2, column=0, sticky="w", **pad)
        ttk.Combobox(
            frame, textvariable=self.button_var,
            values=["left", "right", "middle"], state="readonly", width=8
        ).grid(row=2, column=1, sticky="w", **pad)

        ttk.Label(frame, text="Tipo de clique:").grid(row=3, column=0, sticky="w", **pad)
        ttk.Combobox(
            frame, textvariable=self.click_type_var,
            values=["single", "double"], state="readonly", width=8
        ).grid(row=3, column=1, sticky="w", **pad)

        self.status_label = ttk.Label(
            frame, text="Estado: PARADO", foreground="red",
            font=("Segoe UI", 11, "bold")
        )
        self.status_label.grid(row=4, column=0, columnspan=2, pady=(15, 5))

        self.toggle_button = ttk.Button(frame, text="Iniciar (F6)", command=self.core.toggle)
        self.toggle_button.grid(row=5, column=0, columnspan=2, pady=(5, 0))

        ttk.Label(
            frame, text="Pressiona F6 em qualquer altura para ligar/desligar.",
            font=("Segoe UI", 8), foreground="gray"
        ).grid(row=6, column=0, columnspan=2, pady=(10, 0))

    def _sync_config(self, *_args):
        try:
            self.core.configure(
                interval=float(self.interval_var.get()),
                button=self.button_var.get(),
                click_type=self.click_type_var.get(),
            )
        except (tk.TclError, ValueError):
            pass

    def _on_core_state_change(self, running):
        self.after(0, self._update_status, running)

    def _update_status(self, running):
        if running:
            self.status_label.config(text="Estado: A CLICAR", foreground="green")
            self.toggle_button.config(text="Parar (F6)")
            self.toggle_button.config(state="disabled")
            self.after(400, lambda: self.toggle_button.config(state="normal"))
        else:
            self.status_label.config(text="Estado: PARADO", foreground="red")
            self.toggle_button.config(text="Iniciar (F6)")

    def _on_close(self):
        self.core.shutdown()
        self.destroy()