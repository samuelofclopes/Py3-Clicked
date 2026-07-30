import subprocess
import shutil
import sys

def install_windows_packages():
    print("Sistema Windows detectado.")
    print("Nota: O 'tkinter' já vem embutido no Python do Windows por padrão.")
    print("Instalando 'pynput' usando o pip...\n")
    
    try:
        # No Windows, o pip é seguro e recomendado.
        # sys.executable garante que estamos usando o pip da instalação atual do Python
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
        print("\nSucesso! pynput instalado no Windows.")
    except subprocess.CalledProcessError:
        print("\nErro: Falha ao instalar o pynput via pip no Windows.")

def install_linux_packages():
    print("Sistema Linux detectado. Verificando gerenciadores de pacotes...\n")

    # Mapeamento dos gerenciadores do Linux
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
            print(f"'{manager}' detectado. Tentando instalação...")
            full_command = details["cmd"] + details["packages"]
            
            try:
                subprocess.check_call(full_command)
                print(f"\nSucesso! tkinter e pynput instalados.")
                installed = True
                break
            except subprocess.CalledProcessError:
                print(f"\nErro: {manager} encontrou um problema durante a instalação.")
                break

    if not installed:
        print("\nNão foi possível detectar um gerenciador de pacotes Linux suportado automaticamente.")

if __name__ == "__main__":
    print("Iniciando processo de instalação multiplataforma...\n")
    
    if sys.platform == "win32":
        install_windows_packages()
    elif sys.platform.startswith("linux"):
        install_linux_packages()
    else:
        print(f"Sistema operacional não suportado por este script: {sys.platform}")
    
    print("\nProcesso finalizado.")