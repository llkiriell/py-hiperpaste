"""Localizacion de recursos, valida tanto en fuente como empaquetado."""

import os
import sys


def base_dir() -> str:
    """Carpeta raiz de recursos.

    Bajo PyInstaller los datos se extraen a ``sys._MEIPASS``; ejecutando desde
    el repositorio la raiz es el directorio padre de este paquete.
    """
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return meipass
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def asset_path(name: str) -> str:
    return os.path.join(base_dir(), "assets", name)


def executable_path() -> str:
    """Ruta a invocar para relanzar la aplicacion.

    Empaquetado es el propio .exe. En fuente es pythonw.exe, que evita la
    ventana de consola al abrirse desde el menu contextual.
    """
    if getattr(sys, "frozen", False):
        return sys.executable
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    return pythonw if os.path.exists(pythonw) else sys.executable


def launch_args() -> list:
    """Argumentos que preceden a los propios de la app al relanzarla."""
    if getattr(sys, "frozen", False):
        return []
    return [os.path.join(base_dir(), "main.py")]
