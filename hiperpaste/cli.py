"""Despacho de la linea de comandos.

Un unico ejecutable cubre los cuatro roles: bandeja, pegado desde el menu
contextual, ventana de configuracion y alta/baja en el registro.
"""

import sys

from . import APP_NAME, notify, registry

_USAGE = f"""{APP_NAME}

  {APP_NAME}.exe                 Inicia el icono de bandeja
  {APP_NAME}.exe --tray          Idem
  {APP_NAME}.exe --paste RUTA    Pega el portapapeles en RUTA
  {APP_NAME}.exe --config        Abre la ventana de configuracion
  {APP_NAME}.exe --register      Registra la opcion del menu contextual
  {APP_NAME}.exe --unregister    Retira la opcion del menu contextual
"""

def main(argv=None) -> int:
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
            notify.error(f"Error inesperado al pegar.\n\n{type(exc).__name__}: {exc}")
            return 1
        return 0

    if command in ("--config", "-c"):
        from .ui.settings import open_settings
        open_settings()
        return 0

    if command == "--register":
        registry.register_context_menu()
        return 0

    if command == "--unregister":
        registry.unregister_context_menu()
        return 0

    if command in ("--help", "-h", "/?"):
        notify.info(_USAGE)
        return 0

    notify.warn(f"Opcion desconocida: {command}\n\n{_USAGE}")
    return 2
