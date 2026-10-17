r"""Configuracion persistente en %APPDATA%\Hiperpaste\config.json."""

import json
import os
import tempfile

from . import APP_NAME, keycombo

# Idioma fuente. Vive aqui y no en i18n para no importar en circulo:
# i18n necesita config_dir() para localizar las traducciones del usuario.
DEFAULT_LANGUAGE = "es"

DEFAULTS = {
    "enabled": True,
    "text_format": "txt",      # "txt" | "md"
    "image_format": "png",     # "png" | "jpg"
    "jpg_quality": 92,
    "ask_name_text": False,
    "ask_name_image": False,
    "name_prefix": APP_NAME,
    "start_with_windows": False,
    "language": DEFAULT_LANGUAGE,
    # Atajos globales (ver keycombo.py). Cadena vacia = sin atajo. El de pegar
    # sin formato evita Ctrl+Alt+V, que es el Pegado especial de Office.
    "hotkey_paste": "ctrl+alt+h",
    "hotkey_plain": "ctrl+alt+shift+v",
    "hotkey_copypath": "ctrl+alt+c",
    # Copia de multiples rutas (Hipertools > Copiar ruta)
    "copypath_multi_enabled": False,
    "copypath_multi_limit": 50,
    # Marca de un solo uso del traspaso desde Hiperpegado (ver migrate.py).
    "migrated_from_hiperpegado": False,
}

TEXT_FORMATS = ("txt", "md")
IMAGE_FORMATS = ("png", "jpg")
HOTKEY_KEYS = ("hotkey_paste", "hotkey_plain", "hotkey_copypath")


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

    for key in ("enabled", "ask_name_text", "ask_name_image",
                "start_with_windows", "migrated_from_hiperpegado",
                "copypath_multi_enabled"):
        if isinstance(data.get(key), bool):
            cfg[key] = data[key]

    limit = data.get("copypath_multi_limit")
    if isinstance(limit, (int, float)):
        cfg["copypath_multi_limit"] = max(1, min(500, int(limit)))

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

    # Se acepta cualquier codigo con forma razonable, no una lista cerrada: los
    # idiomas se anaden dejando un .json en la carpeta del usuario, y quien
    # decide si existe es i18n.init(), que cae al espanol si no lo encuentra.
    language = data.get("language")
    if isinstance(language, str) and language.strip():
        cfg["language"] = language.strip()[:16]

    # Una combinacion invalida conserva el valor por defecto; la vacia es una
    # eleccion legitima (atajo desactivado) y se respeta.
    for key in HOTKEY_KEYS:
        combo = keycombo.normalize(data.get(key))
        if combo is not None:
            cfg[key] = combo

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
