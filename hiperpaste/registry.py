"""Integracion con el registro: menu contextual y arranque con Windows.

Todo vive bajo HKEY_CURRENT_USER, por lo que nunca requiere elevacion.
"""

import winreg

from . import APP_NAME
from .i18n import t
from .resources import executable_path, launch_args

# Menu contextual del fondo de carpeta: el clic derecho sobre el espacio
# vacio de una carpeta abierta.
_MENU_KEY = r"Software\Classes\Directory\Background\shell\Hiperpaste"
_COMMAND_KEY = _MENU_KEY + r"\command"
_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_MENU_LABEL = APP_NAME

# Hipertools: submenu agrupador independiente de la entrada de Hiperpaste.
# SubCommands vacio indica al Explorador que las opciones estan en su
# subclave shell.
#
# Oculto desde la 1.1.1: su unica opcion era Pegar sin formato, que actua en
# otras aplicaciones y por eso se usa con su atajo, no desde el Explorador. Se
# conserva para futuras herramientas: basta con anadirlas a _TOOLS_ITEMS y
# activar TOOLS_MENU_VISIBLE. Mientras este oculto, ensure_context_menu retira
# las claves que dejaron las versiones anteriores.
TOOLS_MENU_VISIBLE = False
TOOLS_LABEL = "Hipertools"
_TOOLS_KEY = r"Software\Classes\Directory\Background\shell\Hipertools"
# (subclave, clave de traduccion de la etiqueta, argumentos de la aplicacion).
# Las etiquetas se escriben en el idioma activo: el Explorador no traduce.
_TOOLS_ITEMS = ()


def _quoted_launcher() -> str:
    parts = [executable_path()] + launch_args()
    return " ".join(f'"{part}"' for part in parts)


def context_menu_command() -> str:
    """Comando del menu contextual.

    %V es el token que entrega la carpeta abierta en Directory\Background;
    %1 no funciona en esa clave.
    """
    return f'{_quoted_launcher()} --paste "%V"'


def _tools_enabled() -> bool:
    return TOOLS_MENU_VISIBLE and bool(_TOOLS_ITEMS)


def _tool_keys(subkey: str) -> tuple:
    item_key = rf"{_TOOLS_KEY}\shell\{subkey}"
    return item_key, item_key + r"\command"


def _tool_command(args: str) -> str:
    return f"{_quoted_launcher()} {args}"


def startup_command() -> str:
    return f"{_quoted_launcher()} --tray"


def register_context_menu() -> None:
    icon = f'"{executable_path()}",0'
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _MENU_KEY) as key:
        winreg.SetValueEx(key, None, 0, winreg.REG_SZ, _MENU_LABEL)
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon)
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _COMMAND_KEY) as key:
        winreg.SetValueEx(key, None, 0, winreg.REG_SZ, context_menu_command())
    _register_tools_menu(icon)


def _register_tools_menu(icon: str) -> None:
    # Se rehace desde cero: asi desaparecen las opciones retiradas, o el menu
    # entero si esta oculto.
    _delete_tree(_TOOLS_KEY)
    if not _tools_enabled():
        return
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _TOOLS_KEY) as key:
        winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, TOOLS_LABEL)
        winreg.SetValueEx(key, "SubCommands", 0, winreg.REG_SZ, "")
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon)
    for subkey, label_key, args in _TOOLS_ITEMS:
        item_key, command_key = _tool_keys(subkey)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, item_key) as key:
            winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, t(label_key))
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, command_key) as key:
            winreg.SetValueEx(key, None, 0, winreg.REG_SZ, _tool_command(args))


def _tools_menu_up_to_date() -> bool:
    if not _tools_enabled():
        return not _key_exists(_TOOLS_KEY)
    for subkey, label_key, args in _TOOLS_ITEMS:
        item_key, command_key = _tool_keys(subkey)
        if (_read_value(command_key, None) != _tool_command(args)
                or _read_value(item_key, "MUIVerb") != t(label_key)):
            return False
    return True


def _key_exists(path: str) -> bool:
    try:
        winreg.OpenKey(winreg.HKEY_CURRENT_USER, path).Close()
        return True
    except OSError:
        return False


def _delete_tree(path: str) -> None:
    """Borra una clave con todas sus subclaves (DeleteKey no es recursivo)."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
            children = []
            index = 0
            while True:
                try:
                    children.append(winreg.EnumKey(key, index))
                except OSError:
                    break
                index += 1
    except FileNotFoundError:
        return
    for child in children:
        _delete_tree(path + "\\" + child)
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
    except FileNotFoundError:
        pass


def unregister_context_menu() -> None:
    for path in (_COMMAND_KEY, _MENU_KEY):
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
        except FileNotFoundError:
            pass
    _delete_tree(_TOOLS_KEY)


def _read_value(path: str, name):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
            return winreg.QueryValueEx(key, name)[0]
    except OSError:
        return None


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
    en el HKCU de cada usuario la primera vez que la ejecuta. Tambien pone
    Hipertools al dia: lo retira mientras esta oculto y, visible, rehace sus
    etiquetas si cambio el idioma.
    """
    if (_read_value(_COMMAND_KEY, None) == context_menu_command()
            and _tools_menu_up_to_date()):
        return
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
