"""Icono de bandeja: activar/desactivar, configuracion y salida."""

import pystray
import win32api
import win32event
import winerror
from PIL import Image

from . import APP_NAME, __version__, config, registry
from .resources import asset_path, spawn

_MUTEX_NAME = r"Global\HiperpasteTrayMutex"


def _single_instance_handle():
    """Reserva el mutex de instancia unica, o None si ya hay una corriendo."""
    handle = win32event.CreateMutex(None, False, _MUTEX_NAME)
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        return None
    return handle


def _load_icon(name: str) -> Image.Image:
    try:
        return Image.open(asset_path(name))
    except Exception:
        # Cuadro liso de emergencia si faltan los recursos.
        return Image.new("RGBA", (64, 64), (37, 99, 235, 255))


class Tray:
    def __init__(self):
        self.cfg = config.load()
        self._mtime = config.mtime()
        self._on = _load_icon("icon.ico")
        self._off = _load_icon("icon_off.ico")
        self.icon = pystray.Icon(
            APP_NAME,
            icon=self._on,
            title=self._tooltip(),
            menu=self._build_menu(),
        )

    # -- estado ------------------------------------------------------------
    def _tooltip(self) -> str:
        estado = "Activado" if self.cfg["enabled"] else "Desactivado"
        return f"{APP_NAME} \u2014 {estado}"

    def _sync(self) -> None:
        """Relee la configuracion si cambio en disco (p. ej. desde la ventana)."""
        current = config.mtime()
        if current != self._mtime:
            self._mtime = current
            self.cfg = config.load()

    def _refresh(self) -> None:
        self.icon.icon = self._on if self.cfg["enabled"] else self._off
        self.icon.title = self._tooltip()
        self.icon.update_menu()

    # -- acciones ----------------------------------------------------------
    def _is_enabled(self, _item=None) -> bool:
        self._sync()
        return self.cfg["enabled"]

    def _is_startup(self, _item=None) -> bool:
        return registry.is_run_at_startup()

    def _toggle_enabled(self, _icon=None, _item=None) -> None:
        self._sync()
        self.cfg["enabled"] = not self.cfg["enabled"]
        config.save(self.cfg)
        self._mtime = config.mtime()
        self._refresh()

    def _toggle_startup(self, _icon=None, _item=None) -> None:
        self._sync()
        wanted = not registry.is_run_at_startup()
        registry.set_run_at_startup(wanted)
        self.cfg["start_with_windows"] = wanted
        config.save(self.cfg)
        self._mtime = config.mtime()
        self._refresh()

    def _open_settings(self, _icon=None, _item=None) -> None:
        spawn("--config")

    def _quit(self, _icon=None, _item=None) -> None:
        self.icon.stop()

    # -- menu --------------------------------------------------------------
    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem(f"{APP_NAME} {__version__}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Activado", self._toggle_enabled,
                checked=self._is_enabled, default=True,
            ),
            pystray.MenuItem("Configuracion...", self._open_settings),
            pystray.MenuItem(
                "Iniciar con Windows", self._toggle_startup, checked=self._is_startup,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Salir", self._quit),
        )

    def run(self) -> None:
        self.icon.run()


def run_tray() -> int:
    handle = _single_instance_handle()
    if handle is None:
        # Ya hay una bandeja activa; mostramos su configuracion y salimos.
        spawn("--config")
        return 0

    # Repara la entrada del menu si la aplicacion cambio de ubicacion, y la
    # da de alta la primera vez que cada usuario del equipo la ejecuta.
    try:
        registry.ensure_context_menu()
    except OSError:
        pass

    Tray().run()
    return 0
