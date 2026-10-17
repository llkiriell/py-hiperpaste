"""Comprobacion de actualizaciones contra las releases de GitHub.

Deshabilitada: Hiperpaste todavia no esta publicado, asi que no se hace
ninguna peticion de red. La opcion se muestra igualmente, en gris, y para
activarla basta con rellenar GITHUB_REPO y poner ENABLED a True.

Solo biblioteca estandar, para no anadir una dependencia por esto.
"""

import json
import urllib.request

from . import __version__

ENABLED = True
GITHUB_REPO = "llkiriell/py-hiperpaste"
REPO_URL = f"https://github.com/{GITHUB_REPO}"
RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases"
_LATEST_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

_TIMEOUT = 6.0
_USER_AGENT = f"Hiperpaste/{__version__}"


def parse_version(text: str) -> tuple:
    """Convierte "v1.2.3" en (1, 2, 3), ignorando lo que no sea numerico.

    Tolerante a proposito: la etiqueta de una release la escribe una persona
    y no siempre respeta el formato.
    """
    numeros = []
    for parte in str(text or "").strip().lstrip("vV").split("."):
        digitos = ""
        for caracter in parte:
            if not caracter.isdigit():
                break
            digitos += caracter
        if not digitos:
            break
        numeros.append(int(digitos))
    return tuple(numeros)


def is_newer(latest: str, current: str = __version__) -> bool:
    """True si ``latest`` es posterior a ``current``.

    Una etiqueta ilegible se considera no-novedad: preferimos no avisar a
    avisar en falso.
    """
    nueva = parse_version(latest)
    actual = parse_version(current)
    if not nueva:
        return False
    return nueva > actual


def check_latest(timeout: float = _TIMEOUT) -> dict:
    """Consulta la ultima release publicada.

    Devuelve ``{"version", "url", "is_newer"}``, o ``None`` si la
    comprobacion esta deshabilitada. Los errores de red se propagan para que
    quien llama pueda distinguir "no hay novedades" de "no se pudo mirar".
    """
    if not ENABLED:
        return None

    peticion = urllib.request.Request(
        _LATEST_API,
        headers={
            "User-Agent": _USER_AGENT,
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(peticion, timeout=timeout) as respuesta:
        datos = json.loads(respuesta.read().decode("utf-8"))

    version = str(datos.get("tag_name") or "").lstrip("vV")
    return {
        "version": version,
        "url": datos.get("html_url") or RELEASES_URL,
        "is_newer": is_newer(version),
    }
