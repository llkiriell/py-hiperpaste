"""Integracion con el registro: menu contextual y arranque con Windows.

Todo vive bajo HKEY_CURRENT_USER, por lo que nunca requiere elevacion.
"""

import winreg

from . import APP_NAME
from .resources import executable_path, launch_args

# Menu contextual del fondo de carpeta: el clic derecho sobre el espacio
# vacio de una carpeta abierta.
_MENU_KEY = r"Software\Classes\Directory\Background\shell\Hiperpaste"
_COMMAND_KEY = _MENU_KEY + r"\command"
_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_MENU_LABEL = APP_NAME


def _quoted_launcher() -> str:
    parts = [executable_path()] + launch_args()
    return " ".join(f'"{part}"' for part in parts)


def context_menu_command() -> str:
    """Comando del menu contextual.

    %V es el token que entrega la carpeta abierta en Directory\Background;
    %1 no funciona en esa clave.
    """
    return f'{_quoted_launcher()} --paste "%V"'


def startup_command() -> str:
    return f"{_quoted_launcher()} --tray"


def register_context_menu() -> None:
    icon = f'"{executable_path()}",0'
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _MENU_KEY) as key:
        winreg.SetValueEx(key, None, 0, winreg.REG_SZ, _MENU_LABEL)
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon)
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _COMMAND_KEY) as key:
        winreg.SetValueEx(key, None, 0, winreg.REG_SZ, context_menu_command())


def unregister_context_menu() -> None:
    for path in (_COMMAND_KEY, _MENU_KEY):
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
        except FileNotFoundError:
            pass


def is_context_menu_registered() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _COMMAND_KEY) as key:
            return bool(winreg.QueryValueEx(key, None)[0])
    except OSError:
        return False


def ensure_context_menu() -> None:
    """Registra o repara la entrada.

    Se llama en cada arranque de la bandeja: recrea la clave si la aplicacion
    cambio de ubicacion y, en instalaciones para todo el equipo, la da de alta
    en el HKCU de cada usuario la primera vez que la ejecuta.
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _COMMAND_KEY) as key:
            if winreg.QueryValueEx(key, None)[0] == context_menu_command():
                return
    except OSError:
        pass
    register_context_menu()


def set_run_at_startup(enabled: bool) -> None:
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, startup_command())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass


def is_run_at_startup() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
            return bool(winreg.QueryValueEx(key, APP_NAME)[0])
    except OSError:
        return False
