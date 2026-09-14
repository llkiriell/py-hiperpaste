"""Combinaciones de teclas para los atajos globales.

Una combinacion se guarda como texto canonico, legible en el config.json:
``"ctrl+alt+h"``. Los modificadores van siempre en el mismo orden y la tecla
al final. Las teclas sin nombre propio (las de puntuacion, que cambian con la
distribucion del teclado) se guardan por su codigo virtual: ``"ctrl+alt+vk192"``.

Modulo puro, sin dependencias de la aplicacion, para que config.py pueda
validar los valores sin importar en circulo.
"""

import ctypes

# Constantes de RegisterHotKey.
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000

# Orden canonico de los modificadores: el mismo que muestra Windows.
_MODIFIERS = (("ctrl", MOD_CONTROL), ("alt", MOD_ALT), ("shift", MOD_SHIFT))
_MOD_LABELS = {"ctrl": "Ctrl", "alt": "Alt", "shift": "Shift"}

# Codigos virtuales de los propios modificadores (genericos, izquierda,
# derecha y Windows): nunca pueden ser la tecla principal de un atajo.
MODIFIER_VKS = frozenset((0x10, 0x11, 0x12, 0x5B, 0x5C,
                          0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5))


def _named_keys() -> dict:
    keys = {}
    for code in range(ord("A"), ord("Z") + 1):
        keys[chr(code).lower()] = (code, chr(code))
    for digit in range(10):
        keys[str(digit)] = (0x30 + digit, str(digit))
        keys[f"num{digit}"] = (0x60 + digit, f"Num {digit}")
    for index in range(1, 25):
        keys[f"f{index}"] = (0x6F + index, f"F{index}")
    keys.update({
        # Etiquetas como las serigrafiadas en el teclado, que igual que
        # Ctrl y Shift no se traducen.
        "space": (0x20, "Space"),
        "enter": (0x0D, "Enter"),
        "tab": (0x09, "Tab"),
        "backspace": (0x08, "Backspace"),
        "insert": (0x2D, "Insert"),
        "delete": (0x2E, "Delete"),
        "home": (0x24, "Home"),
        "end": (0x23, "End"),
        "pageup": (0x21, "PageUp"),
        "pagedown": (0x22, "PageDown"),
        "left": (0x25, "←"),
        "up": (0x26, "↑"),
        "right": (0x27, "→"),
        "down": (0x28, "↓"),
        "pause": (0x13, "Pause"),
        "multiply": (0x6A, "Num *"),
        "add": (0x6B, "Num +"),
        "subtract": (0x6D, "Num -"),
        "decimal": (0x6E, "Num ."),
        "divide": (0x6F, "Num /"),
    })
    return keys


_KEYS = _named_keys()
_NAME_BY_VK = {vk: name for name, (vk, _label) in _KEYS.items()}


def parse(combo: str):
    """``"ctrl+alt+h"`` -> ``(mods, vk)``, o ``None`` si no es valida.

    Valida implica al menos Ctrl o Alt: con solo Shift el atajo robaria la
    escritura normal de mayusculas en todas las aplicaciones.
    """
    if not isinstance(combo, str):
        return None
    parts = [part.strip().lower() for part in combo.split("+")]
    if len(parts) < 2 or any(not part for part in parts):
        return None

    *mod_names, key = parts
    mods = 0
    for name in mod_names:
        flag = dict(_MODIFIERS).get(name)
        if flag is None or mods & flag:
            return None
        mods |= flag
    if not mods & (MOD_CONTROL | MOD_ALT):
        return None

    if key in _KEYS:
        vk = _KEYS[key][0]
    elif key.startswith("vk") and key[2:].isdigit():
        vk = int(key[2:])
        if not 0 < vk < 0xFF:
            return None
    else:
        return None
    if vk in MODIFIER_VKS:
        return None
    return mods, vk


def build(mods: int, vk: int):
    """Inverso de ``parse``: texto canonico, o ``None`` si no es valida."""
    names = [name for name, flag in _MODIFIERS if mods & flag]
    key = _NAME_BY_VK.get(vk, f"vk{vk}")
    combo = "+".join(names + [key])
    return combo if parse(combo) else None


def normalize(combo: str):
    """Forma canonica de una combinacion, ``""`` si esta vacia o ``None``."""
    if isinstance(combo, str) and not combo.strip():
        return ""
    parsed = parse(combo)
    return build(*parsed) if parsed else None


def _vk_label(vk: int) -> str:
    """Nombre de una tecla sin entrada en la tabla, segun el teclado activo."""
    try:
        user32 = ctypes.windll.user32
        scan = user32.MapVirtualKeyW(vk, 0)  # MAPVK_VK_TO_VSC
        char = user32.MapVirtualKeyW(vk, 2)  # MAPVK_VK_TO_CHAR
        if char & 0xFFFF:
            return chr(char & 0xFFFF).upper()
        buffer = ctypes.create_unicode_buffer(32)
        if scan and user32.GetKeyNameTextW(scan << 16, buffer, 32):
            return buffer.value
    except (AttributeError, OSError, ValueError):
        pass
    return f"VK {vk}"


def display(combo: str) -> str:
    """Texto para mostrar: ``"Ctrl + Alt + H"``. Vacio si no es valida."""
    parsed = parse(combo)
    if not parsed:
        return ""
    mods, vk = parsed
    labels = [_MOD_LABELS[name] for name, flag in _MODIFIERS if mods & flag]
    name = _NAME_BY_VK.get(vk)
    labels.append(_KEYS[name][1] if name else _vk_label(vk))
    return " + ".join(labels)
