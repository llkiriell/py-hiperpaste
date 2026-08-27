"""Traduccion de los textos visibles.

El espanol es el idioma fuente: sus claves son la referencia y actuan de
respaldo cuando otra traduccion esta incompleta. Los archivos se buscan
primero en la carpeta del usuario, de modo que se puede anadir un idioma a
una instalacion ya compilada sin volver a generarla.
"""

import json
import os

from . import config
from .resources import locale_dir

DEFAULT_CODE = config.DEFAULT_LANGUAGE

# Los archivos que empiezan por guion bajo son plantillas, no idiomas.
_TEMPLATE_PREFIX = "_"

_state = {"code": DEFAULT_CODE, "strings": {}, "fallback": {}}


def user_locale_dir() -> str:
    """Carpeta donde el usuario deja sus propias traducciones."""
    return os.path.join(config.config_dir(), "locales")


def _read(path: str) -> dict:
    """Lee un archivo de idioma. Uno ausente o mal formado devuelve {}.

    Nunca propaga: un JSON roto dejado por un tercero degrada la interfaz al
    espanol, pero no impide arrancar.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items() if isinstance(v, str)}


def _meta(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    meta = data.get("__meta__") if isinstance(data, dict) else None
    return meta if isinstance(meta, dict) else {}


def _candidates(code: str) -> list:
    """Rutas del archivo de un idioma, de mayor a menor prioridad."""
    name = f"{code}.json"
    return [
        os.path.join(user_locale_dir(), name),
        os.path.join(locale_dir(), name),
    ]


def available() -> dict:
    """Idiomas instalados, ``{"es": "Espanol", ...}``, ordenados por nombre.

    Los de la carpeta del usuario pisan a los empaquetados con el mismo
    codigo, lo que permite corregir una traduccion sin recompilar.
    """
    found = {}
    for directory in (locale_dir(), user_locale_dir()):
        try:
            entries = sorted(os.listdir(directory))
        except OSError:
            continue
        for entry in entries:
            if not entry.endswith(".json") or entry.startswith(_TEMPLATE_PREFIX):
                continue
            code = os.path.splitext(entry)[0]
            meta = _meta(os.path.join(directory, entry))
            found[code] = meta.get("name") or code
    return dict(sorted(found.items(), key=lambda item: item[1].lower()))


def init(code: str = None) -> str:
    """Carga el idioma indicado y devuelve el que ha quedado activo.

    Un codigo desconocido o un archivo ilegible caen al espanol, asi que
    borrar una traduccion propia nunca bloquea la aplicacion.
    """
    code = (code or DEFAULT_CODE).strip() or DEFAULT_CODE

    fallback = {}
    for path in _candidates(DEFAULT_CODE):
        fallback = _read(path)
        if fallback:
            break

    strings = fallback
    if code != DEFAULT_CODE:
        strings = {}
        for path in _candidates(code):
            strings = _read(path)
            if strings:
                break
        if not strings:
            code = DEFAULT_CODE
            strings = fallback

    _state.update({"code": code, "strings": strings, "fallback": fallback})
    return code


def current() -> str:
    return _state["code"]


def t(key: str, **kwargs) -> str:
    """Texto de ``key``, con ``{marcador}`` sustituido por los kwargs.

    Cadena de respaldo: idioma activo -> espanol -> la propia clave. Si una
    traduccion trae un marcador que no existe, se usa el texto en espanol en
    lugar de reventar la ventana que lo pide.
    """
    if not _state["strings"] and not _state["fallback"]:
        init(_state["code"])

    spanish = _state["fallback"].get(key, key)
    text = _state["strings"].get(key, spanish)
    if not kwargs:
        return text
    try:
        return text.format(**kwargs)
    except (KeyError, IndexError, ValueError):
        try:
            return spanish.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return spanish
