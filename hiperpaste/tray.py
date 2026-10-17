"""Icono de bandeja: activar/desactivar, configuracion, atajos y salida."""

import ctypes

import pystray
import win32api
import win32event
import winerror
from PIL import Image

from . import (APP_NAME, __version__, config, explorer, hotkeys, i18n,
               keycombo, migrate, notify, plainpaste, registry, updates)
from .i18n import t
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
        self._language = i18n.current()
        self._on = _load_icon("icon.ico")
        self._off = _load_icon("icon_off.ico")
        self.icon = pystray.Icon(
            APP_NAME,
            icon=self._on,
            title=self._tooltip(),
            menu=self._build_menu(),
        )
        self.hotkeys = hotkeys.HotkeyListener(
            {
                "hotkey_paste": self._hotkey_paste,
                "hotkey_plain": self._hotkey_plain,
                "hotkey_copypath": self._hotkey_copypath,
            },
            on_failure=self._hotkey_failed,
        )

    # -- estado ------------------------------------------------------------
    def _tooltip(self) -> str:
        estado = t("tray.state.on" if self.cfg["enabled"] else "tray.state.off")
        return t("tray.tooltip", app=APP_NAME, state=estado)

    def _sync(self) -> None:
        """Relee la configuracion si cambio en disco (p. ej. desde la ventana)."""
        current = config.mtime()
        if current != self._mtime:
            self._mtime = current
            self.cfg = config.load()
            # El idioma se cambia desde la ventana de ajustes, que es otro
            # proceso: al detectarlo hay que rehacer el menu, cuyas etiquetas
            # se resolvieron al construirlo.
            if self.cfg["language"] != self._language:
                self._language = i18n.init(self.cfg["language"])
                self.icon.menu = self._build_menu()

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

    def _open_about(self, _icon=None, _item=None) -> None:
        spawn("--about")

    def _check_updates(self, _icon=None, _item=None) -> None:
        # La comprobacion vive en la ventana Acerca de, que ya la muestra.
        spawn("--about")

    def _quit(self, _icon=None, _item=None) -> None:
        self.hotkeys.stop()
        self.icon.stop()

    # -- atajos ------------------------------------------------------------
    def _notify(self, message: str) -> None:
        try:
            self.icon.notify(message, APP_NAME)
        except Exception:
            pass

    def _hotkey_paste(self) -> None:
        """Pega en la carpeta de la ventana del Explorador activa."""
        folder = explorer.folder_for_window(hotkeys.foreground_window())
        if not folder:
            self._notify(t("hotkey.no_folder"))
            return
        # Quien recibe el atajo puede traer ventanas al frente y ceder ese
        # permiso: sin el, el dialogo de nombre se abriria detras del Explorador.
        ctypes.windll.user32.AllowSetForegroundWindow(-1)  # ASFW_ANY
        spawn("--paste", folder)

    def _hotkey_plain(self) -> None:
        try:
            plainpaste.paste_plain()
        except Exception as exc:
            notify.error(t("paste.unexpected_error",
                           error=f"{type(exc).__name__}: {exc}"))

    def _hotkey_copypath(self) -> None:
        try:
            from .copypath import copy_paths_hotkey
            copy_paths_hotkey(hotkeys.foreground_window(), notifier=self._notify)
        except Exception as exc:
            notify.error(t("paste.unexpected_error",
                           error=f"{type(exc).__name__}: {exc}"))

    def _hotkey_failed(self, combo: str) -> None:
        self._notify(t("hotkey.register_failed", combo=keycombo.display(combo)))

    def _setup(self, icon) -> None:
        # Se arranca aqui y no antes de run(): hasta ahora el icono no existe
        # y no podria mostrar el aviso de un atajo ocupado.
        icon.visible = True
        self.hotkeys.start()

    # -- menu --------------------------------------------------------------
    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem(f"{APP_NAME} {__version__}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                t("tray.enabled"), self._toggle_enabled,
                checked=self._is_enabled, default=True,
            ),
            pystray.MenuItem(t("tray.settings"), self._open_settings),
            pystray.MenuItem(
                t("tray.startup"), self._toggle_startup, checked=self._is_startup,
            ),
            pystray.Menu.SEPARATOR,
            # Visible siempre; pulsable solo cuando haya releases publicadas.
            pystray.MenuItem(
                t("tray.check_updates"), self._check_updates,
                enabled=updates.ENABLED,
            ),
            pystray.MenuItem(t("tray.about", app=APP_NAME), self._open_about),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(t("tray.quit"), self._quit),
        )

    def run(self) -> None:
        self.icon.run(setup=self._setup)


def run_tray() -> int:
    handle = _single_instance_handle()
    if handle is None:
        # Ya hay una bandeja activa; mostramos su configuracion y salimos.
        spawn("--config")
        return 0

    # Traspaso desde Hiperpegado: adopta sus ajustes y retira sus claves,
    # que si no dejarian una segunda entrada muerta en el menu contextual.
    try:
        migrate.run()
    except OSError:
        pass

    # Repara la entrada del menu si la aplicacion cambio de ubicacion, y la
    # da de alta la primera vez que cada usuario del equipo la ejecuta.
    try:
        registry.ensure_context_menu()
    except OSError:
        pass

    Tray().run()
    return 0
