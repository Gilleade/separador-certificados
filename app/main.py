import tkinter as tk

from app.config.app_config import WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from app.gui.main_window import MainWindow
from app.utils.runtime_paths import get_asset_path


def main():
    root = tk.Tk()
    root.title(WINDOW_TITLE)
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.minsize(960, 700)

    icon_path = get_asset_path("app_icon.ico")
    if icon_path.exists():
        try:
            root.iconbitmap(default=str(icon_path))
        except Exception:
            pass

    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "gilleade.separador.certificados"
        )
    except Exception:
        pass

    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()