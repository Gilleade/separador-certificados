import os
import platform
import subprocess


def open_folder(folder_path: str) -> None:
    if not folder_path:
        return

    system_name = platform.system()

    if system_name == "Windows":
        os.startfile(folder_path)
    elif system_name == "Darwin":
        subprocess.run(["open", folder_path], check=False)
    else:
        subprocess.run(["xdg-open", folder_path], check=False)