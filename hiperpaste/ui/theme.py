"""Ajustes comunes de apariencia para las ventanas de la aplicacion."""

import customtkinter as ctk

from ..resources import asset_path

PAD = 16
_initialised = False


def init() -> None:
    global _initialised
    if _initialised:
        return
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    _initialised = True


def apply_icon(window) -> None:
    """Asigna el icono de la aplicacion; silencioso si el .ico no esta."""
    try:
        window.iconbitmap(asset_path("icon.ico"))
    except Exception:
        pass


def fit_and_center(window) -> None:
    """Deja que Tk dimensione la ventana segun su contenido y la centra.

    Fijar el tamano a mano se queda corto en pantallas con otro escalado o
    tamano de fuente del sistema, y el pie de botones acaba fuera de la
    ventana. Aqui solo se impone la posicion: Tk adopta el tamano que pide
    el contenido.
    """
    window.update_idletasks()
    height = window.winfo_reqheight()
    x = (window.winfo_screenwidth() - window.winfo_reqwidth()) // 2
    y = max(0, (window.winfo_screenheight() - height) // 3)
    # Solo posicion: sin tamano, Tk adopta el que pide el contenido.
    window.wm_geometry(f"+{max(0, x)}+{y}")


def grab_focus(window) -> None:
    """Trae la ventana al frente robando el foco al Explorador."""
    window.lift()
    window.attributes("-topmost", True)
    window.after(200, lambda: window.attributes("-topmost", False))
    try:
        window.focus_force()
    except Exception:
        pass
