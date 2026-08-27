"""Genera los iconos de la aplicacion.

Dibuja un portapapeles con un rayo y exporta assets/icon.ico (activo) y
assets/icon_off.ico (atenuado, para el estado desactivado). Para usar un
icono propio basta con sustituir esos dos archivos.
"""

import os
import sys

from PIL import Image, ImageDraw

SIZES = (16, 24, 32, 48, 64, 128, 256)
CANVAS = 512

ACCENT = (37, 99, 235, 255)      # azul del tema
ACCENT_DARK = (29, 78, 216, 255)
PAPER = (255, 255, 255, 255)
BOLT = (250, 190, 45, 255)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")


def draw_icon() -> Image.Image:
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Cuerpo del portapapeles.
    d.rounded_rectangle((96, 104, 416, 464), radius=44, fill=ACCENT)
    # Hoja de papel.
    d.rounded_rectangle((136, 152, 376, 424), radius=26, fill=PAPER)
    # Pinza superior.
    d.rounded_rectangle((188, 56, 324, 132), radius=30, fill=ACCENT_DARK)
    d.rounded_rectangle((216, 76, 296, 112), radius=18, fill=ACCENT)

    # Rayo: el gesto "hiper" del nombre.
    bolt = [
        (286, 178), (196, 306), (250, 306),
        (222, 404), (318, 264), (262, 264),
    ]
    d.polygon(bolt, fill=BOLT)

    return img


def to_ico(image: Image.Image, path: str) -> None:
    image.save(path, format="ICO", sizes=[(s, s) for s in SIZES])


def dim(image: Image.Image) -> Image.Image:
    """Version apagada: escala de grises y menor opacidad."""
    alpha = image.getchannel("A").point(lambda v: int(v * 0.55))
    grey = image.convert("L").convert("RGBA")
    grey.putalpha(alpha)
    return grey


def main() -> int:
    os.makedirs(ASSETS, exist_ok=True)
    icon = draw_icon()
    to_ico(icon, os.path.join(ASSETS, "icon.ico"))
    to_ico(dim(icon), os.path.join(ASSETS, "icon_off.ico"))
    icon.resize((256, 256), Image.LANCZOS).save(os.path.join(ASSETS, "icon.png"))
    print(f"Iconos generados en {ASSETS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
