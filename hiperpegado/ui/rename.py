"""Dialogo modal para editar el nombre del archivo antes de pegarlo."""

import customtkinter as ctk

from .. import APP_NAME
from . import theme

def ask_filename(suggested: str, extension: str) -> str:
    """Pide el nombre del archivo (sin extension).

    Devuelve el nombre elegido, o ``None`` si el usuario cancela, lo que
    aborta el pegado por completo.
    """
    theme.init()
    result = {"value": None}

    window = ctk.CTk()
    window.title(f"{APP_NAME} \u00b7 Nombre del archivo")
    window.resizable(False, False)
    theme.apply_icon(window)

    frame = ctk.CTkFrame(window, fg_color="transparent")
    frame.pack(fill="both", expand=True, padx=theme.PAD, pady=theme.PAD)

    ctk.CTkLabel(
        frame,
        text="Nombre del archivo",
        font=ctk.CTkFont(size=15, weight="bold"),
    ).pack(anchor="w")

    row = ctk.CTkFrame(frame, fg_color="transparent")
    row.pack(fill="x", pady=(12, 0))

    entry = ctk.CTkEntry(row, width=340, height=36, font=ctk.CTkFont(size=13))
    entry.pack(side="left", fill="x", expand=True)
    entry.insert(0, suggested)

    ctk.CTkLabel(
        row,
        text=f".{extension}",
        width=52,
        font=ctk.CTkFont(size=13, weight="bold"),
    ).pack(side="left", padx=(8, 0))

    hint = ctk.CTkLabel(
        frame,
        text="Los caracteres no validos se sustituiran automaticamente.",
        font=ctk.CTkFont(size=11),
        text_color=("gray45", "gray60"),
    )
    hint.pack(anchor="w", pady=(8, 0))

    def accept(_event=None):
        result["value"] = entry.get()
        window.destroy()

    def cancel(_event=None):
        result["value"] = None
        window.destroy()

    buttons = ctk.CTkFrame(frame, fg_color="transparent")
    buttons.pack(side="bottom", fill="x", pady=(14, 0))
    ctk.CTkButton(
        buttons, text="Cancelar", width=110, command=cancel,
        fg_color="transparent", border_width=1,
        text_color=("gray20", "gray85"),
    ).pack(side="right")
    ctk.CTkButton(
        buttons, text="Guardar", width=110, command=accept,
    ).pack(side="right", padx=(0, 8))

    window.bind("<Return>", accept)
    window.bind("<KP_Enter>", accept)
    window.bind("<Escape>", cancel)
    window.protocol("WM_DELETE_WINDOW", cancel)

    theme.fit_and_center(window)
    theme.grab_focus(window)
    # El Explorador tiene el foco al invocarnos; hay que reclamarlo una vez
    # dibujada la ventana o el campo queda inerte.
    def focus_entry():
        entry.focus_set()
        entry.select_range(0, "end")
        entry.icursor("end")

    window.after(120, focus_entry)
    window.mainloop()

    return result["value"]
