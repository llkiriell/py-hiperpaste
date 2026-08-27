"""Configuracion persistente en %APPDATA%\Hiperpaste\config.json."""

import json
import os
import tempfile

from . import APP_NAME

DEFAULTS = {
    "enabled": True,
    "text_format": "txt",      # "txt" | "md"
    "image_format": "png",     # "png" | "jpg"
    "jpg_quality": 92,
    "ask_name_text": False,
    "ask_name_image": False,
    "name_prefix": APP_NAME,
    "start_with_windows": False,
}

TEXT_FORMATS = ("txt", "md")
IMAGE_FORMATS = ("png", "jpg")


def config_dir() -> str:
    appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(appdata, APP_NAME)


def config_path() -> str:
    return os.path.join(config_dir(), "config.json")


def _coerce(data: dict) -> dict:
    """Fusiona con los valores por defecto descartando lo invalido."""
    cfg = dict(DEFAULTS)
    if not isinstance(data, dict):
        return cfg

    for key in ("enabled", "ask_name_text", "ask_name_image", "start_with_windows"):
        if isinstance(data.get(key), bool):
            cfg[key] = data[key]

    if data.get("text_format") in TEXT_FORMATS:
        cfg["text_format"] = data["text_format"]
    if data.get("image_format") in IMAGE_FORMATS:
        cfg["image_format"] = data["image_format"]

    quality = data.get("jpg_quality")
    if isinstance(quality, (int, float)):
        cfg["jpg_quality"] = max(50, min(100, int(quality)))

    prefix = data.get("name_prefix")
    if isinstance(prefix, str) and prefix.strip():
        cfg["name_prefix"] = prefix.strip()

    return cfg


def load() -> dict:
    """Lee la configuracion. Un archivo ausente o corrupto cae a defaults."""
    try:
        with open(config_path(), "r", encoding="utf-8") as fh:
            return _coerce(json.load(fh))
    except (OSError, ValueError):
        return dict(DEFAULTS)


def save(cfg: dict) -> None:
    """Escritura atomica: temporal en la misma carpeta + os.replace."""
    directory = config_dir()
    os.makedirs(directory, exist_ok=True)
    payload = json.dumps(_coerce(cfg), indent=2, ensure_ascii=False)

    handle, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as fh:
            fh.write(payload)
        os.replace(tmp, config_path())
    except OSError:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def mtime() -> float:
    """Marca de tiempo del archivo, 0.0 si no existe. Para detectar cambios."""
    try:
        return os.stat(config_path()).st_mtime
    except OSError:
        return 0.0
