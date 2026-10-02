# Py3-Clicked

A simple, cross-platform autoclicker written in Python 3, for **Linux** and **Windows**.

Pick an interval, a mouse button and a hotkey, then press the hotkey anywhere to start or stop clicking.

## Features

- Adjustable interval between clicks (in seconds)
- Left, right or middle mouse button
- Single or double clicks
- Configurable global hotkey (default: **F6**)
- Settings are saved between sessions
- One-command installer with an application-menu launcher (`.desktop` on Linux, Start Menu shortcut on Windows)

## Requirements

- Python 3.8 or newer
- tkinter (included with Python on Windows; a separate package on most Linux distros)
- [pynput](https://pypi.org/project/pynput/) (installed automatically by the installer)

## Installation

```
python3 install.py
```

On Windows, use `python install.py`.

The installer:

1. checks that tkinter is available,
2. copies the app to your user folder,
3. creates a private virtual environment and installs `pynput` in it,
4. adds a launcher, so you can find **Py3-Clicked** in your applications menu.

Nothing is installed system-wide and no administrator rights are needed.

### Installing tkinter (Linux)

If the installer says tkinter is missing, install it with your package manager:

| Distro                  | Command                           |
| ----------------------- | --------------------------------- |
| Debian / Ubuntu / Mint  | `sudo apt install python3-tk`     |
| Fedora                  | `sudo dnf install python3-tkinter`|
| Arch                    | `sudo pacman -S tk`               |
| openSUSE                | `sudo zypper install python3-tk`  |

### Uninstalling

```
python3 install.py --uninstall            # remove the app, keep your settings
python3 install.py --uninstall --purge    # remove everything, settings included
```

## Run without installing

```
pip install pynput
python3 main.pyw
```

or, from the project folder, `python3 -m py3_clicked`.

## Usage

| Control          | What it does                                                                 |
| ---------------- | ---------------------------------------------------------------------------- |
| **Interval (s)** | Time between clicks, in seconds (must be greater than zero).                 |
| **Mouse button** | `left`, `right` or `middle`.                                                 |
| **Click type**   | `single` or `double`.                                                        |
| **Hotkey**       | Click the button, then press the key you want. `Esc` cancels.                |
| **Start / Stop** | Toggles the autoclicker. The hotkey does the same from any window.           |

Tip: choose a key you don't use for typing, such as an F-key. The hotkey is global, so a letter would toggle the clicker every time you type it.

Invalid values (for example, text in the interval field) are ignored and the last valid value stays in use.

## Settings

Settings are stored as JSON and written when you close the window:

- **Linux:** `~/.config/py3-clicked/settings.json`
- **Windows:** `%APPDATA%\py3-clicked\settings.json`

```json
{
  "interval": 0.1,
  "button": "left",
  "click_type": "single",
  "hotkey": "f6"
}
```

If the file is missing or contains bad values, the defaults are used.

## Project structure

```
Py3-Clicked/
├── py3_clicked/
│   ├── core.py        # clicking logic, hotkey listener, settings
│   ├── ui.py          # tkinter interface
│   ├── paths.py       # where user files live
│   └── __main__.py    # entry point for `python -m py3_clicked`
├── assets/            # application icon (.png / .ico)
├── install.py         # cross-platform installer
├── main.pyw           # run straight from the project folder
└── LICENSE
```

## Compatibility notes

- Developed for Linux (X11 and Wayland, on Debian-based distros) and Windows.
- **Wayland:** `pynput` is built around X11, so on Wayland it may only see input from XWayland windows. The hotkey and the clicks can therefore fail to work system-wide. If that happens, running your session on X11 is the most reliable workaround.
- **Linux install:** `pynput` depends on `evdev`, which may need to be compiled. If `pip` fails, install a C compiler and the Python headers (`python3-dev` / `python3-devel`) and run the installer again.
- Some games and elevated (administrator) windows on Windows may ignore simulated clicks.

## Troubleshooting

| Problem                                | Try this                                                                  |
| -------------------------------------- | ------------------------------------------------------------------------- |
| `No module named tkinter`              | Install tkinter (see the table above).                                    |
| Hotkey does nothing                    | Check the key is not used by another app; see the Wayland note above.     |
| Clicks don't register                  | Same as above, or the target window may be running with higher privileges.|
| Launcher icon looks wrong (Windows)    | Run the installer again; if it persists, restart Explorer to clear the icon cache. |

## Contributing

Found an incompatibility or a bug? Please open an issue and include your OS, desktop environment (X11 or Wayland) and Python version. Pull requests are welcome.

## License

Released under the [GNU General Public License v3.0](LICENSE).