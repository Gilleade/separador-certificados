import tkinter as tk

from app.config.app_config import WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from app.gui.main_window import MainWindow


def main():
    root = tk.Tk()
    root.title(WINDOW_TITLE)
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.minsize(960, 700)

    MainWindow(root)

    root.mainloop()


if __name__ == "__main__":
    main()