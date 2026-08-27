# -*- mode: python ; coding: utf-8 -*-
"""Empaquetado de Hiperpaste (PyInstaller, modo onedir)."""

from PyInstaller.utils.hooks import collect_data_files

# CustomTkinter carga sus temas desde archivos .json en disco; sin incluirlos
# el ejecutable falla al arrancar.
datas = collect_data_files("customtkinter")
datas += [("assets/icon.ico", "assets"), ("assets/icon_off.ico", "assets")]
# icon.png lo muestra la ventana Acerca de; tkinter no dibuja un .ico ahi.
datas += [("assets/icon.png", "assets")]

# Los idiomas se leen de disco en tiempo de ejecucion: sin incluirlos aqui el
# ejecutable solo entiende las claves, no los textos.
datas += [("locales/*.json", "locales")]

# El entorno de desarrollo trae muchos paquetes pesados que no usa la
# aplicacion; sin excluirlos el bundle se dispara de tamano.
excludes = [
    "numpy", "scipy", "pandas", "matplotlib", "IPython", "pytest",
    "PyQt5", "PyQt6", "PySide2", "PySide6", "wx",
    "torch", "tensorflow", "sklearn", "cv2", "notebook",
]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=["pystray._win32", "PIL._tkinter_finder"],
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Hiperpaste",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    # Sin consola: el menu contextual lanza el proceso en cada clic derecho y
    # una ventana negra parpadeando seria inaceptable.
    console=False,
    disable_windowed_traceback=False,
    icon="assets/icon.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    # onedir y no onefile: onefile descomprime a %TEMP% en cada invocacion,
    # anadiendo cerca de un segundo de latencia a cada pegado.
    name="Hiperpaste",
)
