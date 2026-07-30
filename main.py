"""
Junta core com a interface.
É o ficheiro executavel.
"""

from ui import AutoClickerGUI


def main():
    app = AutoClickerGUI()
    app.mainloop()


if __name__ == "__main__":
    main()