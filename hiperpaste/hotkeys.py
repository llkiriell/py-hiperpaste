"""Atajos de teclado globales, atendidos desde el proceso de la bandeja.

RegisterHotKey entrega WM_HOTKEY a la cola del hilo que lo registro, y ese
hilo necesita su propio bucle de mensajes: pystray ya ocupa el principal.
"""

import ctypes
import threading
from ctypes import wintypes

from . import config, i18n, keycombo

_user32 = ctypes.WinDLL("user32", use_last_error=True)
_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

_user32.RegisterHotKey.argtypes = (wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT)
_user32.RegisterHotKey.restype = wintypes.BOOL
_user32.UnregisterHotKey.argtypes = (wintypes.HWND, ctypes.c_int)
_user32.UnregisterHotKey.restype = wintypes.BOOL
_user32.GetMessageW.argtypes = (ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT)
_user32.GetMessageW.restype = wintypes.BOOL
_user32.SetTimer.argtypes = (wintypes.HWND, ctypes.c_size_t, wintypes.UINT, ctypes.c_void_p)
_user32.SetTimer.restype = ctypes.c_size_t
_user32.KillTimer.argtypes = (wintypes.HWND, ctypes.c_size_t)
_user32.PostThreadMessageW.argtypes = (wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
_user32.GetForegroundWindow.restype = wintypes.HWND

_WM_QUIT = 0x0012
_WM_TIMER = 0x0113
_WM_HOTKEY = 0x0312
# Cada cuanto se mira si la ventana de ajustes (otro proceso) guardo cambios
# o esta capturando una combinacion.
_RELOAD_MS = 250

# Identificador de RegisterHotKey por clave de configuracion.
_IDS = {"hotkey_paste": 1, "hotkey_plain": 2}

# Mientras exista, la bandeja suelta sus atajos: Windows entrega un atajo
# registrado a su dueno antes que a la ventana activa, y el modal de captura
# no podria recibir la combinacion que se quiere reasignar.
_CAPTURE_MUTEX = r"Local\HiperpasteHotkeyCapture"
_SYNCHRONIZE = 0x00100000

_kernel32.CreateMutexW.argtypes = (ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR)
_kernel32.CreateMutexW.restype = wintypes.HANDLE
_kernel32.OpenMutexW.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR)
_kernel32.OpenMutexW.restype = wintypes.HANDLE
_kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)


class capture_pause:
    """Contexto que pausa los atajos de la bandeja mientras dura."""

    def __enter__(self):
        self._handle = _kernel32.CreateMutexW(None, False, _CAPTURE_MUTEX)
        return self

    def __exit__(self, *_exc):
        if self._handle:
            _kernel32.CloseHandle(self._handle)
            self._handle = None


def _capture_in_progress() -> bool:
    handle = _kernel32.OpenMutexW(_SYNCHRONIZE, False, _CAPTURE_MUTEX)
    if not handle:
        return False
    _kernel32.CloseHandle(handle)
    return True


def is_available(combo: str) -> bool:
    """Prueba si otra aplicacion tiene ya tomada la combinacion."""
    parsed = keycombo.parse(combo)
    if not parsed:
        return False
    mods, vk = parsed
    probe_id = 0xBFFF
    if not _user32.RegisterHotKey(None, probe_id, mods | keycombo.MOD_NOREPEAT, vk):
        return False
    _user32.UnregisterHotKey(None, probe_id)
    return True


def foreground_window() -> int:
    return _user32.GetForegroundWindow() or 0


class HotkeyListener:
    """Hilo que mantiene los atajos al dia con la configuracion guardada.

    ``actions`` asocia cada clave de configuracion a la funcion que ejecuta;
    cada disparo corre en un hilo de trabajo aparte para no bloquear el bucle
    de mensajes. ``on_failure(combo)`` avisa de una combinacion ocupada.
    """

    def __init__(self, actions: dict, on_failure=None):
        self._actions = actions
        self._on_failure = on_failure
        self._thread = None
        self._thread_id = 0
        self._ready = threading.Event()
        self._registered = {}
        self._warned = set()
        self._busy = threading.Lock()
        self._mtime = None
        self._cfg = None

    # -- ciclo de vida -----------------------------------------------------
    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, name="hotkeys", daemon=True)
        self._thread.start()
        self._ready.wait(2)

    def stop(self) -> None:
        if self._thread_id:
            _user32.PostThreadMessageW(self._thread_id, _WM_QUIT, 0, 0)
        if self._thread:
            self._thread.join(2)

    # -- hilo de mensajes --------------------------------------------------
    def _run(self) -> None:
        self._thread_id = _kernel32.GetCurrentThreadId()
        # Crea la cola de mensajes del hilo antes de que stop() pueda escribir
        # en ella: PostThreadMessage falla sobre un hilo que aun no la tiene.
        msg = wintypes.MSG()
        _user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0)
        self._reload()
        timer = _user32.SetTimer(None, 0, _RELOAD_MS, None)
        self._ready.set()
        try:
            while _user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                if msg.message == _WM_HOTKEY:
                    self._fire(msg.wParam)
                elif msg.message == _WM_TIMER:
                    self._reload()
        finally:
            _user32.KillTimer(None, timer)
            self._unregister_all()

    def _reload(self) -> None:
        current = config.mtime()
        if current != self._mtime:
            self._mtime = current
            self._cfg = config.load()
            self._warned.clear()
            if self._cfg["language"] != i18n.current():
                i18n.init(self._cfg["language"])
        cfg = self._cfg

        # Desactivado, los atajos se sueltan para que la combinacion llegue a
        # la aplicacion activa como si Hiperpaste no existiera.
        # Una combinacion ocupada no se reintenta hasta que cambie la
        # configuracion: se volveria a registrar todo cuatro veces por segundo.
        wanted = {}
        if cfg["enabled"] and not _capture_in_progress():
            wanted = {key: cfg[key] for key in _IDS
                      if cfg[key] and cfg[key] not in self._warned}
        if wanted == self._registered:
            return

        self._unregister_all()
        for key, combo in wanted.items():
            mods, vk = keycombo.parse(combo)
            if _user32.RegisterHotKey(None, _IDS[key], mods | keycombo.MOD_NOREPEAT, vk):
                self._registered[key] = combo
            else:
                self._warned.add(combo)
                if self._on_failure:
                    self._on_failure(combo)

    def _unregister_all(self) -> None:
        for key in list(self._registered):
            _user32.UnregisterHotKey(None, _IDS[key])
        self._registered.clear()

    def _fire(self, hotkey_id: int) -> None:
        key = next((k for k, v in _IDS.items() if v == hotkey_id), None)
        action = self._actions.get(key)
        # Un disparo a la vez: mantener pulsado o repetir el atajo mientras un
        # pegado sigue en curso no debe encadenar pegados.
        if action is None or not self._busy.acquire(blocking=False):
            return

        def work():
            try:
                action()
            finally:
                self._busy.release()

        threading.Thread(target=work, name=f"hotkey-{key}", daemon=True).start()
