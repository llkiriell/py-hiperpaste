"""Dialogo modal que captura la combinacion de teclas de un atajo."""

import customtkinter as ctk
import win32api

from .. import APP_NAME, hotkeys, keycombo
from ..i18n import t
from . import theme

_MUTED = ("gray45", "gray60")
_ERROR = ("#b42318", "#f97066")

_VK_ESCAPE = 0x1B
_VK_RETURN = 0x0D
# Modificador -> teclas que lo activan (generica, izquierda y derecha).
_MOD_KEYS = (
    (keycombo.MOD_CONTROL, (0x11, 0xA2, 0xA3)),
    (keycombo.MOD_ALT, (0x12, 0xA4, 0xA5)),
    (keycombo.MOD_SHIFT, (0x10, 0xA0, 0xA1)),
)
_MOD_LABELS = ((keycombo.MOD_CONTROL, "Ctrl"), (keycombo.MOD_ALT, "Alt"),
               (keycombo.MOD_SHIFT, "Shift"))


def _held_modifiers() -> int:
    # Se consulta al sistema y no a event.state: tkinter en Windows confunde
    # AltGr y no siempre refleja Alt en el propio evento que lo pulsa.
    # GetKeyState y no GetAsyncKeyState: da el estado cuando se genero el
    # mensaje, no el de ahora, y una pulsacion rapida ya estaria soltada.
    mods = 0
    for flag, keys in _MOD_KEYS:
        if any(win32api.GetKeyState(vk) & 0x8000 for vk in keys):
            mods |= flag
    return mods


def ask_hotkey(parent, action: str, current: str, default: str,
               reserved: dict) -> str:
    """Pide una combinacion para ``action``.

    ``reserved`` asocia las combinaciones ya asignadas a otras acciones con el
    nombre de esas acciones. Devuelve la combinacion canonica, ``""`` para
    dejar la accion sin atajo o ``None`` si el usuario cancela.
    """
    result = {"value": None}
    state = {"pending": current}

    window = ctk.CTkToplevel(parent)
    window.title(t("hotkey.title", app=APP_NAME))
    window.resizable(False, False)
    window.transient(parent)
    # CTkToplevel impone su propio icono a los 200 ms; se reasigna despues.
    window.after(250, lambda: theme.apply_icon(window))

    frame = ctk.CTkFrame(window, fg_color="transparent")
    frame.pack(fill="both", expand=True, padx=theme.PAD, pady=theme.PAD)

    ctk.CTkLabel(
        frame, text=t("hotkey.heading", action=action),
        font=ctk.CTkFont(size=15, weight="bold"), anchor="w",
    ).pack(anchor="w")
    ctk.CTkLabel(
        frame, text=t("hotkey.instruction"), font=ctk.CTkFont(size=12),
        text_color=_MUTED, anchor="w", justify="left",
    ).pack(anchor="w", pady=(4, 0))

    shown = ctk.CTkLabel(
        frame, text="", height=64, width=360, corner_radius=8,
        fg_color=("gray90", "gray20"), font=ctk.CTkFont(size=20, weight="bold"),
    )
    shown.pack(fill="x", pady=(14, 0))

    status = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=12),
                          text_color=_ERROR, anchor="w", justify="left")
    status.pack(anchor="w", pady=(8, 0))

    buttons = ctk.CTkFrame(frame, fg_color="transparent")
    buttons.pack(fill="x", pady=(10, 0))

    def label_for(combo: str) -> str:
        return keycombo.display(combo) if combo else t("settings.hotkey_none")

    def problem(combo: str):
        """Motivo por el que no se puede usar ``combo``, o ``None``."""
        if not combo:
            return None
        if combo in reserved:
            return t("hotkey.reserved", action=reserved[combo])
        # La bandeja suelta sus atajos mientras este dialogo esta abierto, asi
        # que la prueba solo tropieza con los de otras aplicaciones.
        if not hotkeys.is_available(combo):
            return t("hotkey.in_use")
        return None

    def offer(combo: str) -> None:
        shown.configure(text=label_for(combo))
        reason = problem(combo)
        status.configure(text=reason or "")
        if reason:
            accept_button.configure(state="disabled")
        else:
            state["pending"] = combo
            accept_button.configure(state="normal")

    def accept(_event=None):
        if accept_button.cget("state") == "disabled":
            return
        result["value"] = state["pending"]
        window.destroy()

    def cancel(_event=None):
        result["value"] = None
        window.destroy()

    def on_key(event):
        vk = event.keycode
        mods = _held_modifiers()
        if vk in keycombo.MODIFIER_VKS:
            # Combinacion a medias: se muestra lo que va pulsado.
            held = [name for flag, name in _MOD_LABELS if mods & flag]
            shown.configure(text=" + ".join(held + ["…"]))
            status.configure(text="")
            return "break"
        if not mods & (keycombo.MOD_CONTROL | keycombo.MOD_ALT):
            if vk == _VK_ESCAPE:
                cancel()
            elif vk == _VK_RETURN:
                accept()
            else:
                shown.configure(text=label_for(state["pending"]))
                status.configure(text=t("hotkey.invalid"))
            return "break"
        combo = keycombo.build(mods, vk)
        if combo is None:
            status.configure(text=t("hotkey.invalid"))
        else:
            offer(combo)
        return "break"

    def on_release(event):
        # Soltar los modificadores sin tecla principal devuelve la vista a la
        # ultima combinacion valida.
        if event.keycode in keycombo.MODIFIER_VKS and not _held_modifiers():
            if shown.cget("text").endswith("…"):
                shown.configure(text=label_for(state["pending"]))

    ctk.CTkButton(
        buttons, text=t("hotkey.clear"), width=0, command=lambda: offer(""),
        fg_color="transparent", hover=False, text_color=_MUTED,
    ).pack(side="left")
    ctk.CTkButton(
        buttons, text=t("hotkey.reset"), width=0, command=lambda: offer(default),
        fg_color="transparent", hover=False, text_color=_MUTED,
    ).pack(side="left", padx=(8, 0))
    ctk.CTkButton(
        buttons, text=t("hotkey.cancel"), width=100, command=cancel,
        fg_color="transparent", border_width=1, text_color=("gray20", "gray85"),
    ).pack(side="right")
    accept_button = ctk.CTkButton(buttons, text=t("hotkey.accept"), width=100,
                                  command=accept)
    accept_button.pack(side="right", padx=(0, 8))

    shown.configure(text=label_for(current))
    window.bind("<KeyPress>", on_key)
    window.bind("<KeyRelease>", on_release)
    window.protocol("WM_DELETE_WINDOW", cancel)

    with hotkeys.capture_pause():
        theme.fit_and_center(window)
        window.wait_visibility()
        window.grab_set()
        window.focus_force()
        parent.wait_window(window)

    return result["value"]
