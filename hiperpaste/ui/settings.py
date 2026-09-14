"""Ventana de configuracion de Hiperpaste."""

import customtkinter as ctk

from .. import APP_NAME, __version__, config, i18n, keycombo, registry
from ..i18n import t
from ..paste import timestamp_stem
from ..resources import spawn
from . import theme
from .hotkey_capture import ask_hotkey

_MUTED = ("gray45", "gray60")


def _section(parent, title: str) -> ctk.CTkFrame:
    ctk.CTkLabel(
        parent,
        text=title,
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color=_MUTED,
    ).pack(anchor="w", padx=4, pady=(14, 4))
    frame = ctk.CTkFrame(parent)
    frame.pack(fill="x")
    return frame


def _row(parent) -> ctk.CTkFrame:
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=14, pady=9)
    return row


def _label(row, text: str) -> ctk.CTkLabel:
    label = ctk.CTkLabel(row, text=text, font=ctk.CTkFont(size=13), anchor="w")
    label.pack(side="left")
    return label


def open_settings() -> None:
    theme.init()
    cfg = config.load()

    window = ctk.CTk()
    window.title(t("settings.title", app=APP_NAME))
    window.resizable(False, False)
    theme.apply_icon(window)

    body = ctk.CTkFrame(window, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=theme.PAD, pady=(theme.PAD, 10))

    ctk.CTkLabel(
        body,
        text=APP_NAME,
        font=ctk.CTkFont(size=20, weight="bold"),
        anchor="w",
    ).pack(anchor="w")
    ctk.CTkLabel(
        body,
        text=t("app.tagline"),
        font=ctk.CTkFont(size=12),
        text_color=_MUTED,
        anchor="w",
    ).pack(anchor="w")

    # Dos columnas: en una sola, la ventana ya no cabe en pantallas de 1080 p
    # desde que existe la seccion de atajos.
    columns = ctk.CTkFrame(body, fg_color="transparent")
    columns.pack(fill="both", expand=True)
    # uniform iguala el ancho de ambas a la mas exigente.
    columns.grid_columnconfigure((0, 1), weight=1, uniform="settings")
    left = ctk.CTkFrame(columns, fg_color="transparent")
    left.grid(row=0, column=0, sticky="new")
    right = ctk.CTkFrame(columns, fg_color="transparent")
    right.grid(row=0, column=1, sticky="new", padx=(theme.PAD, 0))

    # --- Texto -------------------------------------------------------------
    text_frame = _section(left, t("settings.section.text"))

    row = _row(text_frame)
    _label(row, t("settings.file_format"))
    text_format = ctk.CTkSegmentedButton(row, values=[".txt", ".md"], width=150)
    text_format.set("." + cfg["text_format"])
    text_format.pack(side="right")

    row = _row(text_frame)
    _label(row, t("settings.ask_name"))
    ask_text = ctk.CTkSwitch(row, text="")
    ask_text.select() if cfg["ask_name_text"] else ask_text.deselect()
    ask_text.pack(side="right")

    # --- Imagen ------------------------------------------------------------
    image_frame = _section(left, t("settings.section.image"))

    row = _row(image_frame)
    _label(row, t("settings.file_format"))
    image_format = ctk.CTkSegmentedButton(row, values=[".png", ".jpg"], width=150)
    image_format.set("." + cfg["image_format"])
    image_format.pack(side="right")

    quality_row = ctk.CTkFrame(image_frame, fg_color="transparent")
    _label(quality_row, t("settings.jpg_quality"))
    quality_value = ctk.CTkLabel(
        quality_row, text=str(cfg["jpg_quality"]), width=32,
        font=ctk.CTkFont(size=13, weight="bold"),
    )
    quality_value.pack(side="right")
    quality = ctk.CTkSlider(quality_row, from_=50, to=100, number_of_steps=50, width=170)
    quality.set(cfg["jpg_quality"])
    quality.pack(side="right", padx=(0, 10))

    ask_image_row = _row(image_frame)
    _label(ask_image_row, t("settings.ask_name"))
    ask_image = ctk.CTkSwitch(ask_image_row, text="")
    ask_image.select() if cfg["ask_name_image"] else ask_image.deselect()
    ask_image.pack(side="right")

    # --- General -----------------------------------------------------------
    general = _section(right, t("settings.section.general"))

    row = _row(general)
    _label(row, t("settings.language"))
    languages = i18n.available()
    # El desplegable muestra el nombre del idioma y la configuracion guarda su
    # codigo, asi que hace falta tambien el camino de vuelta.
    codes = {name: code for code, name in languages.items()}
    language = ctk.CTkOptionMenu(row, values=list(codes), width=150)
    language.set(languages.get(cfg["language"], languages.get(i18n.DEFAULT_CODE, "")))
    language.pack(side="right")

    row = _row(general)
    _label(row, t("settings.name_prefix"))
    prefix = ctk.CTkEntry(row, width=190)
    prefix.insert(0, cfg["name_prefix"])
    prefix.pack(side="right")

    row = _row(general)
    _label(row, t("settings.startup"))
    startup = ctk.CTkSwitch(row, text="")
    startup.select() if registry.is_run_at_startup() else startup.deselect()
    startup.pack(side="right")

    row = _row(general)
    _label(row, t("settings.enabled", app=APP_NAME))
    enabled = ctk.CTkSwitch(row, text="")
    enabled.select() if cfg["enabled"] else enabled.deselect()
    enabled.pack(side="right")

    # --- Atajos de teclado -------------------------------------------------
    shortcuts = _section(right, t("settings.section.hotkeys"))
    hotkey_values = {key: cfg[key] for key in config.HOTKEY_KEYS}
    hotkey_names = {
        "hotkey_paste": t("settings.hotkey_paste", app=APP_NAME),
        "hotkey_plain": t("settings.hotkey_plain"),
    }

    def hotkey_text(key: str) -> str:
        combo = hotkey_values[key]
        return keycombo.display(combo) if combo else t("settings.hotkey_none")

    def change_hotkey(key: str, button) -> None:
        # La otra accion no puede compartir combinacion: solo una la recibiria.
        reserved = {combo: hotkey_names[other]
                    for other, combo in hotkey_values.items()
                    if other != key and combo}
        chosen = ask_hotkey(window, hotkey_names[key], hotkey_values[key],
                            config.DEFAULTS[key], reserved)
        if chosen is not None:
            hotkey_values[key] = chosen
            button.configure(text=hotkey_text(key))

    for key in config.HOTKEY_KEYS:
        row = _row(shortcuts)
        _label(row, hotkey_names[key])
        button = ctk.CTkButton(
            row, width=190, fg_color="transparent", border_width=1,
            text_color=("gray20", "gray85"),
        )
        button.configure(text=hotkey_text(key),
                         command=lambda k=key, b=button: change_hotkey(k, b))
        button.pack(side="right")

    ctk.CTkLabel(
        shortcuts, text=t("settings.hotkey_hint", app=APP_NAME),
        font=ctk.CTkFont(size=11), text_color=_MUTED, anchor="w", justify="left",
        wraplength=380,
    ).pack(anchor="w", padx=14, pady=(0, 9))

    # --- Vista previa ------------------------------------------------------
    preview_frame = _section(left, t("settings.section.preview"))
    preview = ctk.CTkLabel(
        preview_frame, text="", font=ctk.CTkFont(size=12), anchor="w",
        justify="left", text_color=_MUTED,
    )
    preview.pack(anchor="w", padx=14, pady=10)

    def refresh(*_args):
        stem = timestamp_stem(prefix.get().strip() or APP_NAME)
        preview.configure(
            text=f"{stem}{text_format.get()}\n{stem}{image_format.get()}"
        )
        # El deslizador de calidad solo tiene sentido con JPEG. Se inserta
        # antes del interruptor para conservar el orden visual de la seccion.
        if image_format.get() == ".jpg":
            quality_row.pack(fill="x", padx=14, pady=(0, 9), before=ask_image_row)
        else:
            quality_row.pack_forget()
        quality_value.configure(text=str(int(quality.get())))

    text_format.configure(command=refresh)
    image_format.configure(command=refresh)
    quality.configure(command=refresh)
    prefix.bind("<KeyRelease>", refresh)
    refresh()

    ctk.CTkLabel(
        body,
        text=t("settings.hint_windows11"),
        font=ctk.CTkFont(size=11),
        text_color=_MUTED,
        justify="left",
        anchor="w",
    ).pack(anchor="w", pady=(14, 0))

    # --- Botonera ----------------------------------------------------------
    footer = ctk.CTkFrame(window, fg_color="transparent")
    footer.pack(fill="x", padx=theme.PAD, pady=(0, theme.PAD))

    ctk.CTkButton(
        footer, text=f'{t("settings.about")}  v{__version__}',
        command=lambda: spawn("--about"),
        fg_color="transparent", hover=False, width=0, anchor="w",
        font=ctk.CTkFont(size=11), text_color=_MUTED,
    ).pack(side="left")

    def cancel():
        window.destroy()

    def save():
        chosen_language = codes.get(language.get(), cfg["language"])
        updated = dict(cfg)
        updated.update({
            "language": chosen_language,
            "text_format": text_format.get().lstrip("."),
            "image_format": image_format.get().lstrip("."),
            "jpg_quality": int(quality.get()),
            "ask_name_text": bool(ask_text.get()),
            "ask_name_image": bool(ask_image.get()),
            "name_prefix": prefix.get().strip() or APP_NAME,
            "enabled": bool(enabled.get()),
            "start_with_windows": bool(startup.get()),
        })
        updated.update(hotkey_values)
        config.save(updated)
        registry.set_run_at_startup(updated["start_with_windows"])
        # Las etiquetas de Hipertools se escriben en el idioma activo: hay que
        # cargar el recien elegido antes de reparar el menu contextual.
        i18n.init(chosen_language)
        registry.ensure_context_menu()
        window.destroy()
        # Los textos ya dibujados no se retraducen en caliente, asi que la
        # ventana se vuelve a abrir en el idioma recien elegido.
        if chosen_language != cfg["language"]:
            spawn("--config")

    ctk.CTkButton(
        footer, text=t("settings.cancel"), width=110, command=cancel,
        fg_color="transparent", border_width=1, text_color=("gray20", "gray85"),
    ).pack(side="right")
    ctk.CTkButton(footer, text=t("settings.save"), width=110, command=save).pack(
        side="right", padx=(0, 8)
    )

    window.bind("<Escape>", lambda _e: cancel())
    theme.fit_and_center(window)
    theme.grab_focus(window)
    window.mainloop()
