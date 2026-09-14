"""Pegar sin formato: limpia el portapapeles y pega en la ventana activa.

No crea archivos. Deja en el portapapeles solo el texto Unicode, sin HTML,
RTF, enlaces ni metadatos, y simula un Ctrl+V normal.
"""

import time

import win32api
import win32con

from . import APP_NAME, clipboard, config, notify
from .i18n import t

_VK_V = 0x56
# Teclas que el usuario puede seguir pulsando al disparar el atajo.
_HELD_KEYS = (win32con.VK_CONTROL, win32con.VK_MENU, win32con.VK_SHIFT,
              win32con.VK_LWIN, win32con.VK_RWIN)
_RELEASE_TIMEOUT = 1.0
_POLL = 0.02


def _is_down(vk: int) -> bool:
    return bool(win32api.GetAsyncKeyState(vk) & 0x8000)


def _wait_for_release() -> None:
    """Espera a que se suelten los modificadores del atajo.

    Si Alt o Shift siguieran pulsados, el Ctrl+V sintetico llegaria como
    Ctrl+Alt+Shift+V: volveria a disparar el atajo en lugar de pegar. Pasado
    el plazo se liberan a mano.
    """
    deadline = time.monotonic() + _RELEASE_TIMEOUT
    while time.monotonic() < deadline:
        if not any(_is_down(vk) for vk in _HELD_KEYS):
            return
        time.sleep(_POLL)
    for vk in _HELD_KEYS:
        if _is_down(vk):
            win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)


def _send_ctrl_v() -> None:
    up = win32con.KEYEVENTF_KEYUP
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(_VK_V, 0, 0, 0)
    win32api.keybd_event(_VK_V, 0, up, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, up, 0)


def clean_clipboard() -> bool:
    """Reduce el portapapeles a texto plano. ``False`` si no habia texto."""
    text = clipboard.read_text()
    if text is None:
        return False
    clipboard.set_text(text)
    return True


def paste_plain() -> None:
    """Punto de entrada del atajo de Pegar sin formato y de --paste-plain."""
    if not config.load()["enabled"]:
        notify.info(t("paste.disabled", app=APP_NAME))
        return

    try:
        has_text = clean_clipboard()
    except clipboard.ClipboardBusy:
        notify.error(t("paste.clipboard_busy"))
        return
    except Exception as exc:
        notify.error(t("paste.clipboard_error", error=exc))
        return

    if not has_text:
        notify.info(t("plain.no_text"))
        return

    _wait_for_release()
    _send_ctrl_v()
