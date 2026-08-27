"""Ventana Acerca de: nombre, version y comprobacion de actualizaciones."""

import webbrowser

import customtkinter as ctk
from PIL import Image

from .. import APP_NAME, __version__, updates
from ..i18n import t
from ..resources import asset_path
from . import theme

_MUTED = ("gray45", "gray60")
_LINK = ("#2563EB", "#60A5FA")
_LOGO = 96


def _logo(parent) -> None:
    """Dibuja el icono. Si falta el recurso, simplemente no se muestra."""
    try:
        imagen = Image.open(asset_path("icon.png"))
    except Exception:
        return
    ctk.CTkLabel(
        parent,
        text="",
        image=ctk.CTkImage(light_image=imagen, dark_image=imagen,
                           size=(_LOGO, _LOGO)),
    ).pack(pady=(0, 10))


def open_about() -> None:
    theme.init()

    window = ctk.CTk()
    window.title(t("about.title", app=APP_NAME))
    window.resizable(False, False)
    theme.apply_icon(window)

    body = ctk.CTkFrame(window, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=theme.PAD * 2, pady=theme.PAD)

    _logo(body)

    ctk.CTkLabel(
        body, text=APP_NAME, font=ctk.CTkFont(size=22, weight="bold"),
    ).pack()
    ctk.CTkLabel(
        body, text=t("about.version", version=__version__),
        font=ctk.CTkFont(size=12), text_color=_MUTED,
    ).pack(pady=(2, 0))
    ctk.CTkLabel(
        body, text=t("app.tagline"), font=ctk.CTkFont(size=12),
        wraplength=320, justify="center",
    ).pack(pady=(12, 0))
    ctk.CTkLabel(
        body, text=t("about.license"), font=ctk.CTkFont(size=11),
        text_color=_MUTED,
    ).pack(pady=(10, 0))

    repository = ctk.CTkLabel(
        body, text=t("about.repository"), font=ctk.CTkFont(size=11, underline=True),
        text_color=_LINK, cursor="hand2",
    )
    repository.pack(pady=(2, 0))
    repository.bind("<Button-1>", lambda _e: webbrowser.open(updates.RELEASES_URL))

    # --- Actualizaciones ---------------------------------------------------
    status = ctk.CTkLabel(
        body, text="", font=ctk.CTkFont(size=11), text_color=_MUTED,
        wraplength=320, justify="center",
    )

    def check() -> None:
        button.configure(state="disabled", text=t("updates.checking"))
        window.update_idletasks()
        try:
            latest = updates.check_latest()
        except Exception as exc:
            status.configure(text=t("updates.error", error=exc))
        else:
            if latest is None:
                status.configure(text=t("updates.disabled"))
            elif latest["is_newer"]:
                status.configure(text=t("updates.available", **latest))
            else:
                status.configure(text=t("updates.up_to_date", version=__version__))
        button.configure(state="normal", text=t("updates.check"))
        theme.fit_and_center(window)

    button = ctk.CTkButton(body, text=t("updates.check"), width=190, command=check)
    button.pack(pady=(16, 0))

    # Visible pero inerte mientras no haya releases publicadas: la opcion
    # existe, y se explica por que no se puede usar todavia.
    if not updates.ENABLED:
        button.configure(state="disabled")
        status.configure(text=t("updates.not_published"))

    status.pack(pady=(8, 0))

    # --- Cierre ------------------------------------------------------------
    ctk.CTkButton(
        body, text=t("about.close"), width=110, command=window.destroy,
        fg_color="transparent", border_width=1, text_color=("gray20", "gray85"),
    ).pack(pady=(18, 0))

    window.bind("<Escape>", lambda _e: window.destroy())
    theme.fit_and_center(window)
    theme.grab_focus(window)
    window.mainloop()
