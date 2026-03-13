import sys
from pathlib import Path

from app.config.app_config import RUNTIME_FOLDER_NAME


def get_application_base_dir() -> Path:
    """
    Retorna a pasta base da aplicação.

    - Em desenvolvimento: raiz do projeto
    - No executável portátil: pasta onde está o .exe
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[2]


def get_assets_dir() -> Path:
    return get_application_base_dir() / "assets"


def get_asset_path(filename: str) -> Path:
    return get_assets_dir() / filename


def get_runtime_dir() -> Path:
    runtime_dir = get_application_base_dir() / RUNTIME_FOLDER_NAME
    runtime_dir.mkdir(parents=True, exist_ok=True)
    return runtime_dir


def get_runtime_file_path(filename: str) -> Path:
    return get_runtime_dir() / filename