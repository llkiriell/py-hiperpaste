"""Lectura del portapapeles de Windows."""

import io
import struct
import time
from dataclasses import dataclass

import win32clipboard
import win32con
from PIL import Image

# Cabecera BITMAPFILEHEADER: 'BM', tamano total, dos reservados, offset a pixeles.
_BMP_HEADER = struct.Struct("<2sIHHI")
_BMP_HEADER_SIZE = 14


@dataclass
class ClipboardItem:
    kind: str      # "image" | "text" | "files" | "empty"
    payload: object = None


class ClipboardBusy(Exception):
    """El portapapeles quedo bloqueado por otro proceso."""


def _open_clipboard(attempts: int = 5, delay: float = 0.05) -> None:
    """Abre el portapapeles reintentando.

    Es un recurso global de la sesion: otra aplicacion puede tenerlo abierto
    justo en ese instante, y el fallo es transitorio.
    """
    last = None
    for _ in range(attempts):
        try:
            win32clipboard.OpenClipboard()
            return
        except Exception as exc:  # pywintypes.error
            last = exc
            time.sleep(delay)
    raise ClipboardBusy(str(last))


def _dib_to_image(data: bytes) -> Image.Image:
    """Antepone la cabecera BMP que el portapapeles omite y abre con Pillow."""
    if len(data) < 4:
        raise ValueError("DIB truncado")

    header_size = struct.unpack_from("<I", data, 0)[0]
    offset = _BMP_HEADER_SIZE + header_size

    # Las paletas de color van entre la cabecera y los pixeles; hay que
    # sumarlas al offset o la imagen sale desplazada.
    if header_size >= 40:
        bit_count = struct.unpack_from("<H", data, 14)[0]
        used = struct.unpack_from("<I", data, 32)[0]
        if bit_count <= 8:
            offset += (used or (1 << bit_count)) * 4
        else:
            compression = struct.unpack_from("<I", data, 16)[0]
            if compression == 3 and header_size == 40:  # BI_BITFIELDS
                offset += 12

    header = _BMP_HEADER.pack(b"BM", _BMP_HEADER_SIZE + len(data), 0, 0, offset)
    image = Image.open(io.BytesIO(header + data))
    image.load()
    return image


def _read_image() -> Image.Image:
    """Devuelve la imagen del portapapeles, de mayor a menor fidelidad."""
    # Las aplicaciones modernas (navegadores, Figma) publican PNG ademas del
    # DIB. Es la unica variante que conserva el canal alfa.
    png_format = win32clipboard.RegisterClipboardFormat("PNG")
    if png_format and win32clipboard.IsClipboardFormatAvailable(png_format):
        try:
            data = win32clipboard.GetClipboardData(png_format)
            image = Image.open(io.BytesIO(data))
            image.load()
            return image
        except Exception:
            pass

    for fmt in (win32con.CF_DIBV5, win32con.CF_DIB):
        if win32clipboard.IsClipboardFormatAvailable(fmt):
            try:
                return _dib_to_image(win32clipboard.GetClipboardData(fmt))
            except Exception:
                continue

    raise ValueError("No se pudo decodificar la imagen del portapapeles")


def read() -> ClipboardItem:
    """Lee el portapapeles y clasifica su contenido.

    La imagen tiene prioridad sobre el texto: copiar una imagen desde el
    navegador deja tambien texto y HTML, mientras que copiar texto nunca
    produce un DIB.
    """
    _open_clipboard()
    try:
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
            paths = win32clipboard.GetClipboardData(win32con.CF_HDROP)
            return ClipboardItem("files", list(paths))

        png_format = win32clipboard.RegisterClipboardFormat("PNG")
        has_image = (
            win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIBV5)
            or win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB)
            or (png_format and win32clipboard.IsClipboardFormatAvailable(png_format))
        )
        if has_image:
            return ClipboardItem("image", _read_image())

        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            if text:
                return ClipboardItem("text", text)

        return ClipboardItem("empty")
    finally:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass
