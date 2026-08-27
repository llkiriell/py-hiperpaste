"""Materializa el contenido del portapapeles como archivo en una carpeta."""

import os
import re
from datetime import datetime

from PIL import Image

from . import clipboard, config, notify

# Caracteres prohibidos en nombres de archivo de Windows, mas los de control.
_INVALID = re.compile(r'[<>:"/\|?*\x00-\x1f]')
_MAX_STEM = 200
_MAX_COLLISIONS = 999


def timestamp_stem(prefix: str, moment: datetime = None) -> str:
    """Nombre base con la fecha primero, para que ordene cronologicamente."""
    moment = moment or datetime.now()
    return f"{moment:%Y-%m-%d_%H-%M-%S}_{prefix}"


def sanitize(stem: str, fallback: str) -> str:
    """Depura un nombre escrito a mano hasta dejarlo valido para Windows."""
    cleaned = _INVALID.sub(" ", stem or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # Windows rechaza los nombres terminados en punto o espacio.
    cleaned = cleaned.rstrip(". ")
    cleaned = cleaned[:_MAX_STEM].rstrip(". ")
    return cleaned or fallback


def unique_path(folder: str, stem: str, extension: str) -> str:
    """Resuelve colisiones con el sufijo ' (n)' que usa el propio Explorador."""
    candidate = os.path.join(folder, f"{stem}.{extension}")
    if not os.path.exists(candidate):
        return candidate
    for index in range(1, _MAX_COLLISIONS + 1):
        candidate = os.path.join(folder, f"{stem} ({index}).{extension}")
        if not os.path.exists(candidate):
            return candidate
    raise OSError(f"Demasiados archivos con el nombre '{stem}'")


def _write_text(path: str, text: str) -> None:
    # BOM y saltos CRLF: sin ellos el Bloc de notas de Windows 10 muestra los
    # acentos corruptos y el texto en una sola linea.
    normalised = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        fh.write(normalised)


def _write_image(path: str, image: Image.Image, extension: str, quality: int) -> None:
    if extension == "png":
        image.save(path, "PNG", optimize=True)
        return

    # JPEG no admite transparencia: componer sobre blanco antes de convertir,
    # o Pillow lanza OSError.
    if image.mode in ("RGBA", "LA", "P"):
        image = image.convert("RGBA")
        canvas = Image.new("RGB", image.size, (255, 255, 255))
        canvas.paste(image, mask=image.split()[-1])
        image = canvas
    elif image.mode != "RGB":
        image = image.convert("RGB")

    image.save(path, "JPEG", quality=quality, subsampling=0, optimize=True)


def paste_into(folder: str) -> None:
    """Punto de entrada de la opcion del menu contextual."""
    cfg = config.load()

    if not cfg["enabled"]:
        notify.info(
            "Hiperpegado esta desactivado.\n\n"
            "Activalo desde su icono en la bandeja del sistema."
        )
        return

    if not folder or not os.path.isdir(folder):
        notify.error("No se pudo determinar la carpeta de destino.")
        return

    try:
        item = clipboard.read()
    except clipboard.ClipboardBusy:
        notify.error(
            "Otra aplicacion esta usando el portapapeles.\n\n"
            "Espera un momento y vuelve a intentarlo."
        )
        return
    except Exception as exc:
        notify.error(f"No se pudo leer el portapapeles.\n\n{exc}")
        return

    if item.kind == "empty":
        notify.info("El portapapeles esta vacio.\n\nCopia un texto o una imagen primero.")
        return

    if item.kind == "files":
        count = len(item.payload)
        notify.info(
            f"El portapapeles contiene {count} archivo(s).\n\n"
            "Hiperpegado solo convierte texto e imagenes. "
            "Usa el Pegar normal de Windows (Ctrl+V) para copiarlos aqui."
        )
        return

    if item.kind == "image":
        extension = cfg["image_format"]
        ask = cfg["ask_name_image"]
    else:
        extension = cfg["text_format"]
        ask = cfg["ask_name_text"]

    stem = timestamp_stem(cfg["name_prefix"])

    if ask:
        from .ui.rename import ask_filename

        chosen = ask_filename(stem, extension)
        if chosen is None:
            return
        stem = sanitize(chosen, stem)

    try:
        path = unique_path(folder, stem, extension)
        if item.kind == "image":
            _write_image(path, item.payload, extension, cfg["jpg_quality"])
        else:
            _write_text(path, item.payload)
    except PermissionError:
        notify.error(
            "No tienes permiso para escribir en esta carpeta.\n\n"
            f"{folder}"
        )
    except OSError as exc:
        notify.error(f"No se pudo guardar el archivo.\n\n{exc}")
