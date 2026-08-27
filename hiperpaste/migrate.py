"""Traspaso desde la instalacion previa, cuando la aplicacion se llamaba
Hiperpegado.

Se ejecuta una sola vez, al arrancar la bandeja. Sin esto quedarian dos
entradas en el menu contextual —una apuntando a un ejecutable que ya no
existe— y la configuracion del usuario se perderia, porque tanto la carpeta
de ajustes como el valor de arranque derivan del nombre de la aplicacion.
"""

import json
import os
import winreg

from . import config, registry

_OLD_NAME = "Hiperpegado"
_OLD_MENU_KEY = r"Software\Classes\Directory\Background\shell" + "\\" + _OLD_NAME
_OLD_COMMAND_KEY = _OLD_MENU_KEY + r"\command"

_FLAG = "migrated_from_hiperpegado"


def _old_config_path() -> str:
    appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(appdata, _OLD_NAME, "config.json")


def _old_run_entry() -> bool:
    """True si Hiperpegado estaba dado de alta en el arranque de Windows."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry._RUN_KEY) as key:
            return bool(winreg.QueryValueEx(key, _OLD_NAME)[0])
    except OSError:
        return False


def _delete_old_run_entry() -> None:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry._RUN_KEY,
                            0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, _OLD_NAME)
    except OSError:
        pass


def _delete_old_menu_keys() -> None:
    for path in (_OLD_COMMAND_KEY, _OLD_MENU_KEY):
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
        except OSError:
            pass


def _inherit_config(cfg: dict) -> dict:
    """Adopta los ajustes antiguos si aun no hay unos propios.

    Se pasan por config.save(), que valida y descarta lo que no reconoce, de
    modo que un archivo manipulado a mano no puede colarse entero.
    """
    if os.path.exists(config.config_path()):
        return cfg
    try:
        with open(_old_config_path(), "r", encoding="utf-8") as fh:
            previo = json.load(fh)
    except (OSError, ValueError):
        return cfg
    return dict(previo) if isinstance(previo, dict) else cfg


def run() -> None:
    """Migra si procede. Idempotente: deja una marca en la configuracion."""
    cfg = config.load()
    if cfg.get(_FLAG):
        return

    arrancaba = _old_run_entry()
    cfg = _inherit_config(cfg)
    cfg[_FLAG] = True
    config.save(cfg)

    _delete_old_menu_keys()
    if arrancaba:
        _delete_old_run_entry()
        registry.set_run_at_startup(True)
