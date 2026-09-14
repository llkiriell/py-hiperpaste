"""Carpeta abierta en la ventana del Explorador que tiene el foco."""

import os

import pythoncom
import win32com.client
import win32gui
from win32com.shell import shell, shellcon

_EXPLORER_CLASSES = ("CabinetWClass", "ExploreWClass")
# El escritorio es la ventana Progman, o un WorkerW si hay fondo animado.
_DESKTOP_CLASSES = ("Progman", "WorkerW")


def _active_tab(hwnd: int) -> int:
    """Ventana de la pestana visible (Windows 11): la primera en orden Z."""
    try:
        return win32gui.FindWindowEx(hwnd, 0, "ShellTabWindowClass", None)
    except win32gui.error:
        return 0


def _browser_window(window) -> int:
    """Ventana de la pestana a la que pertenece un elemento de Shell.Windows."""
    try:
        provider = window._oleobj_.QueryInterface(pythoncom.IID_IServiceProvider)
        browser = provider.QueryService(shell.SID_STopLevelBrowser,
                                        shell.IID_IShellBrowser)
        return browser.GetWindow()
    except pythoncom.com_error:
        return 0


def _explorer_path(hwnd: int):
    # Con pestanas, todas las de una ventana comparten HWND: se distingue la
    # visible por su ventana de navegador. Si no se puede, vale la primera.
    matches = []
    for window in win32com.client.Dispatch("Shell.Application").Windows():
        try:
            if int(window.HWND) == hwnd:
                matches.append(window)
        except (pythoncom.com_error, AttributeError):
            continue
    if not matches:
        return None

    tab = _active_tab(hwnd)
    chosen = next((w for w in matches if tab and _browser_window(w) == tab),
                  matches[0])
    try:
        return chosen.Document.Folder.Self.Path
    except (pythoncom.com_error, AttributeError):
        return None


def folder_for_window(hwnd: int):
    """Ruta de la carpeta que muestra ``hwnd``, o ``None``.

    ``None`` si la ventana no es del Explorador o muestra una ubicacion
    virtual (Este equipo, Papelera), donde no se puede crear un archivo.
    """
    try:
        cls = win32gui.GetClassName(hwnd)
    except win32gui.error:
        return None

    if cls in _DESKTOP_CLASSES:
        path = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOPDIRECTORY, 0, 0)
    elif cls in _EXPLORER_CLASSES:
        pythoncom.CoInitialize()
        try:
            path = _explorer_path(hwnd)
        finally:
            pythoncom.CoUninitialize()
    else:
        return None

    return path if path and os.path.isdir(path) else None
