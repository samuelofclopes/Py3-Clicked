"""Localização dos ficheiros do utilizador (sem dependências externas)."""
import os
import sys
from pathlib import Path

APP_ID = "py3-clicked"


def config_dir():
    """Pasta de configuração do utilizador, onde o programa pode sempre escrever."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / APP_ID


def settings_file():
    return config_dir() / "settings.json"
