# Py3-Clicked
A Python 3 autoclicker for Linux & Windows. Press **F6** anywhere to start/stop.

## Install
```
python3 install.py
```
This checks for tkinter, creates a private virtualenv with `pynput`, and adds
a launcher (`.desktop` on Linux, Start Menu shortcut on Windows).
Then search for **Py3-Clicked** in your applications menu.

Uninstall: `python3 install.py --uninstall` (add `--purge` to also delete settings).

## Run without installing
```
pip install pynput
python3 main.pyw
```

## Notes
- Settings are stored in `~/.config/py3-clicked/` (Linux) or `%APPDATA%\py3-clicked\` (Windows).
- tkinter is the only system dependency (`sudo apt install python3-tk`, `sudo dnf install python3-tkinter`, `sudo pacman -S tk`).
- On Linux, pynput depends on `evdev`, which may need a C compiler and the Python headers (`python3-dev`).
- Wayland: pynput only sees input from XWayland windows, so F6 and clicks may not work system-wide. Please report incompatibilities!

## Why
With the importance of an autoclicker in modern society, I was forced to create my own.
