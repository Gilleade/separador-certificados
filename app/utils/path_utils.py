import os
import platform
import subprocess


def open_path(path_value: str) -> None:
    if not path_value:
        return

    system_name = platform.system()

    if system_name == "Windows":
        os.startfile(path_value)
    elif system_name == "Darwin":
        subprocess.run(["open", path_value], check=False)
    else:
        subprocess.run(["xdg-open", path_value], check=False)


def open_folder(folder_path: str) -> None:
    open_path(folder_path)