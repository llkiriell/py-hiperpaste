"""Funcionalidad de copia de rutas de archivos (Hipertools > Copiar ruta)."""

import os

from . import APP_NAME, clipboard, config, explorer, notify
from .i18n import t


def copy_paths_hotkey(hwnd: int, notifier=None) -> None:
    """Disparado por el atajo de teclado global.

    Determina los archivos seleccionados en la ventana del Explorador o
    Escritorio activa y los copia al portapapeles.
    """
    cfg = config.load()
    if not cfg["enabled"]:
        msg = t("paste.disabled", app=APP_NAME)
        if notifier:
            notifier(msg)
        else:
            notify.info(msg)
        return

    paths = explorer.selected_paths_for_window(hwnd)
    if not paths:
        msg = t("copypath.no_selection")
        if notifier:
            notifier(msg)
        else:
            notify.info(msg)
        return

    _copy_paths_list(paths, cfg, notifier=notifier)


def copy_path_cli(target_path: str) -> None:
    """Disparado por el menu contextual de Windows (Hipertools > Copiar ruta).

    ``target_path`` es la ruta entregada por Windows (%1). Si la copia
    multiple esta activada, se comprueba si la ventana del Explorador
    tiene varios archivos seleccionados para copiarlos todos juntos.
    """
    if not target_path or not target_path.strip():
        notify.info(t("copypath.no_selection"))
        return

    cfg = config.load()
    norm_target = os.path.abspath(target_path)

    if not cfg.get("copypath_multi_enabled", False):
        # Modo simple: copia unicamente la ruta pulsada
        clipboard.set_text(norm_target)
        return

    # Si la copia multiple esta habilitada, comprobamos si hay seleccion multiple
    # en la ventana activa del Explorador.
    try:
        from .hotkeys import foreground_window
        active_hwnd = foreground_window()
        selected = explorer.selected_paths_for_window(active_hwnd)
        if len(selected) > 1 and any(os.path.abspath(p).lower() == norm_target.lower() for p in selected):
            _copy_paths_list(selected, cfg, notifier=None)
            return
    except Exception:
        pass

    # Si no habia seleccion multiple o fallo la consulta COM, copiamos el archivo unico
    clipboard.set_text(norm_target)


def _copy_paths_list(paths: list[str], cfg: dict, notifier=None) -> None:
    """Copia la lista de rutas respetando las opciones de configuracion."""
    # Normalizar rutas absolutas
    normalized = [os.path.abspath(p) for p in paths if p and p.strip()]
    if not normalized:
        if notifier:
            notifier(t("copypath.no_selection"))
        return

    multi_enabled = cfg.get("copypath_multi_enabled", False)
    limit = cfg.get("copypath_multi_limit", 50)

    if len(normalized) == 1 or not multi_enabled:
        # Copia simple
        clipboard.set_text(normalized[0])
        if notifier:
            if len(normalized) > 1 and not multi_enabled:
                notifier(t("copypath.copied_single_multi_disabled"))
            else:
                notifier(t("copypath.copied_single"))
        return

    # Copia multiple activada
    count = len(normalized)
    exceeded = count > limit
    to_copy = normalized[:limit] if exceeded else normalized

    text_to_clip = "\r\n".join(to_copy)
    clipboard.set_text(text_to_clip)

    if exceeded:
        msg = t("copypath.copied_limit", limit=limit, total=count)
        if notifier:
            notifier(msg)
        else:
            notify.warn(msg)
    elif notifier:
        notifier(t("copypath.copied_multiple", count=count))

