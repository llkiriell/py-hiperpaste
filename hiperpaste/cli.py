"""Despacho de la linea de comandos.

Un unico ejecutable cubre todos los roles: bandeja, pegado desde el menu
contextual, pegado sin formato, ventana de configuracion, Acerca de y
alta/baja en el registro.
"""

import sys

from . import APP_NAME, config, i18n, notify, registry
from .i18n import t


def _usage() -> str:
    return t("cli.usage", app=APP_NAME)


def main(argv=None) -> int:
    # Un unico punto de carga del idioma: cubre los cinco roles del
    # ejecutable, incluido el proceso efimero que atiende el menu contextual.
    i18n.init(config.load()["language"])

    argv = list(sys.argv[1:] if argv is None else argv)
    command = argv[0] if argv else "--tray"

    if command in ("--tray", "-t"):
        from .tray import run_tray
        return run_tray()

    if command in ("--paste", "-p"):
        from .paste import paste_into
        folder = argv[1] if len(argv) > 1 else ""
        try:
            paste_into(folder)
        except Exception as exc:  # ultima red: nunca morir en silencio
            notify.error(t("paste.unexpected_error",
                           error=f"{type(exc).__name__}: {exc}"))
            return 1
        return 0

    if command == "--paste-plain":
        from .plainpaste import paste_plain
        try:
            paste_plain()
        except Exception as exc:
            notify.error(t("paste.unexpected_error",
                           error=f"{type(exc).__name__}: {exc}"))
            return 1
        return 0

    if command in ("--config", "-c"):
        from .ui.settings import open_settings
        open_settings()
        return 0

    if command in ("--about", "-a"):
        from .ui.about import open_about
        open_about()
        return 0

    if command == "--register":
        registry.register_context_menu()
        return 0

    if command == "--unregister":
        registry.unregister_context_menu()
        return 0

    if command in ("--help", "-h", "/?"):
        notify.info(_usage())
        return 0

    notify.warn(t("cli.unknown_option", command=command) + "\n\n" + _usage())
    return 2
