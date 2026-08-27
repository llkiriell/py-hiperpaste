"""Avisos al usuario mediante cuadros de dialogo nativos.

El proceso de pegado es efimero y no dispone del icono de bandeja, asi que
usa MessageBox en lugar de globos de notificacion.
"""

import win32api
import win32con

from . import APP_NAME

_FLAGS = win32con.MB_OK | win32con.MB_TOPMOST | win32con.MB_SETFOREGROUND


def info(message: str, title: str = APP_NAME) -> None:
    win32api.MessageBox(0, message, title, _FLAGS | win32con.MB_ICONINFORMATION)


def warn(message: str, title: str = APP_NAME) -> None:
    win32api.MessageBox(0, message, title, _FLAGS | win32con.MB_ICONWARNING)


def error(message: str, title: str = APP_NAME) -> None:
    win32api.MessageBox(0, message, title, _FLAGS | win32con.MB_ICONERROR)
