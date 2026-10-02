#!/usr/bin/env python3
"""
Py3-Clicked installer for Linux and Windows (standard library only).

    python3 install.py              install
    python3 install.py --uninstall  remove (keeps your settings)
    python3 install.py --uninstall --purge   remove everything, settings included

What it does:
  1. checks that tkinter exists (the only thing that depends on the system);
  2. copies the app to the user folder;
  3. creates a venv and installs pynput there (same on every distro);
  4. creates the launcher: .desktop on Linux, .lnk (Start Menu) on Windows.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent
sys.path.insert(0, str(SOURCE))
from py3_clicked.paths import APP_ID, config_dir  # noqa: E402

APP_NAME = "Py3-Clicked"
IS_WINDOWS = sys.platform == "win32"
IS_LINUX = sys.platform.startswith("linux")

# The only distro-specific part: tkinter can't be installed via pip.
TK_HINTS = {
    "apt": "sudo apt install python3-tk",
    "dnf": "sudo dnf install python3-tkinter",
    "pacman": "sudo pacman -S tk",
    "zypper": "sudo zypper install python3-tk",
    "apk": "sudo apk add py3-tkinter",
}


# ---------- locations ----------

def install_dir() -> Path:
    if IS_WINDOWS:
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / APP_NAME
    base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / APP_ID


def venv_python(windowed=False) -> Path:
    venv = install_dir() / "venv"
    if IS_WINDOWS:
        return venv / "Scripts" / ("pythonw.exe" if windowed else "python.exe")
    return venv / "bin" / "python"


def desktop_file() -> Path:
    base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "applications" / f"{APP_ID}.desktop"


def start_menu_shortcut() -> Path:
    appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    return appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs" / f"{APP_NAME}.lnk"


# ---------- helpers ----------

def run(cmd):
    print("  $", " ".join(str(c) for c in cmd))
    subprocess.check_call([str(c) for c in cmd])


def fail(message):
    print(f"\nError: {message}", file=sys.stderr)
    sys.exit(1)


def check_tkinter():
    try:
        import tkinter  # noqa: F401
        return
    except ImportError:
        pass
    if IS_WINDOWS:
        fail("tkinter is not available. Reinstall Python and keep the "
             "'tcl/tk and IDLE' option checked.")
    for manager, command in TK_HINTS.items():
        if shutil.which(manager):
            fail(f"tkinter is not installed. Run:\n\n    {command}\n\nand then run the installer again.")
    fail("tkinter is not installed. Install your distro's Python tkinter package.")


# ---------- installation ----------

def copy_app():
    target = install_dir()
    target.mkdir(parents=True, exist_ok=True)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    for name in ("py3_clicked", "assets"):
        dest = target / name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(SOURCE / name, dest, ignore=ignore)


def create_venv_and_deps():
    venv = install_dir() / "venv"
    if not venv_python().exists():
        try:
            run([sys.executable, "-m", "venv", venv])
        except subprocess.CalledProcessError:
            hint = " (Debian/Ubuntu: sudo apt install python3-venv)" if IS_LINUX else ""
            fail(f"could not create the virtual environment{hint}.")
    try:
        run([venv_python(), "-m", "pip", "install", "--upgrade", "pynput"])
    except subprocess.CalledProcessError:
        hint = ""
        if IS_LINUX:
            hint = ("\nOn Linux, pynput depends on 'evdev', which may need to be compiled. "
                    "Install a compiler (gcc) and the Python headers "
                    "(python3-dev / python3-devel), then try again.")
        fail(f"failed to install pynput.{hint}")


def create_linux_shortcut():
    icon = install_dir() / "assets" / "icon.png"
    path = desktop_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        f"Name={APP_NAME}\n"
        "Comment=Autoclicker\n"
        f'Exec="{venv_python()}" -m py3_clicked\n'
        f"Path={install_dir()}\n"
        f"Icon={icon}\n"
        "Terminal=false\n"
        "Categories=Utility;\n",
        encoding="utf-8",
    )
    path.chmod(0o755)
    if shutil.which("update-desktop-database"):
        subprocess.call(["update-desktop-database", str(path.parent)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  Launcher created: {path}")


def _ps_quote(value) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def create_windows_shortcut():
    lnk = start_menu_shortcut()
    lnk.parent.mkdir(parents=True, exist_ok=True)
    script = (
        "$s = (New-Object -ComObject WScript.Shell).CreateShortcut("
        f"{_ps_quote(lnk)}); "
        f"$s.TargetPath = {_ps_quote(venv_python(windowed=True))}; "  # pythonw: no console window
        "$s.Arguments = '-m py3_clicked'; "
        f"$s.WorkingDirectory = {_ps_quote(install_dir())}; "
        f"$s.IconLocation = {_ps_quote(str(install_dir() / 'assets' / 'icon.ico') + ',0')}; "
        "$s.Save()"
    )
    try:
        run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script])
    except (subprocess.CalledProcessError, FileNotFoundError):
        fail("could not create the Start Menu shortcut.")
    print(f"  Shortcut created: {lnk}")


def install():
    print(f"Installing {APP_NAME} to {install_dir()}\n")
    check_tkinter()
    copy_app()
    create_venv_and_deps()
    if IS_WINDOWS:
        create_windows_shortcut()
    else:
        create_linux_shortcut()
    print(f"\nDone! Look for '{APP_NAME}' in your applications menu.")


def uninstall(purge):
    for path in (desktop_file(), start_menu_shortcut()):
        if path.exists():
            path.unlink()
            print(f"  Removed: {path}")
    if install_dir().exists():
        shutil.rmtree(install_dir())
        print(f"  Removed: {install_dir()}")
    if purge and config_dir().exists():
        shutil.rmtree(config_dir())
        print(f"  Removed: {config_dir()}")
    print("\nUninstalled.")


def main():
    if not (IS_WINDOWS or IS_LINUX):
        fail(f"unsupported system: {sys.platform}")
    parser = argparse.ArgumentParser(description=f"{APP_NAME} installer")
    parser.add_argument("--uninstall", action="store_true", help="remove the program")
    parser.add_argument("--purge", action="store_true",
                        help="with --uninstall, also delete the settings")
    args = parser.parse_args()
    if args.purge and not args.uninstall:
        parser.error("--purge only makes sense with --uninstall")
    uninstall(args.purge) if args.uninstall else install()


if __name__ == "__main__":
    main()