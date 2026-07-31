import subprocess
import shutil
import sys

def install_windows_packages():
    print("Windows system detected.")
    print("Note: 'tkinter' is already built-in to Windows Python by default.")
    print("Installing 'pynput' using pip...\n")
    
    try:
        # On Windows, pip is safe and recommended.
        # sys.executable ensures we are using the pip from the current Python installation
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
        print("\nSuccess! pynput installed on Windows.")
    except subprocess.CalledProcessError:
        print("\nError: Failed to install pynput via pip on Windows.")

def install_linux_packages():
    print("Linux system detected. Checking package managers...\n")

    # Mapping of Linux package managers
    managers = {
        "apt-get": {
            "cmd": ["sudo", "apt-get", "install", "-y"],
            "packages": ["python3-tk", "python3-pynput"]
        },
        "dnf": {
            "cmd": ["sudo", "dnf", "install", "-y"],
            "packages": ["python3-tkinter", "python3-pynput"]
        },
        "pacman": {
            "cmd": ["sudo", "pacman", "-S", "--noconfirm"],
            "packages": ["tk", "python-pynput"] 
        }
    }

    installed = False

    for manager, details in managers.items():
        if shutil.which(manager):
            print(f"'{manager}' detected. Attempting installation...")
            full_command = details["cmd"] + details["packages"]
            
            try:
                subprocess.check_call(full_command)
                print(f"\nSuccess! tkinter and pynput installed.")
                installed = True
                break
            except subprocess.CalledProcessError:
                print(f"\nError: {manager} encountered a problem during installation.")
                break

    if not installed:
        print("\nCould not automatically detect a supported Linux package manager.")

if __name__ == "__main__":
    print("Starting cross-platform installation process...\n")
    
    if sys.platform == "win32":
        install_windows_packages()
    elif sys.platform.startswith("linux"):
        install_linux_packages()
    else:
        print(f"Operating system not supported by this script: {sys.platform}")
    
    print("\nProcess finished.")