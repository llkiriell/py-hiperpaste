"""Genera el ejecutable y el instalador de Hiperpegado.

    python build.py            iconos + ejecutable + instalador
    python build.py --no-installer   se detiene tras el ejecutable
"""

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist", "Hiperpegado")
ISS = os.path.join(ROOT, "installer", "hiperpegado.iss")

# winget instala Inno Setup en %LOCALAPPDATA%\Programs; el instalador
# oficial lo pone en Archivos de programa. Hay que contemplar ambos.
ISCC_CANDIDATES = (
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Inno Setup 6", "ISCC.exe"),
    r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    r"C:\Program Files\Inno Setup 6\ISCC.exe",
)


def step(message: str) -> None:
    print(f"\n=== {message} ", "=" * max(0, 60 - len(message)), sep="")


def run(command: list) -> None:
    print("  $", " ".join(command))
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        sys.exit(f"\nFallo: {command[0]} devolvio {result.returncode}")


def find_iscc() -> str:
    for path in ISCC_CANDIDATES:
        if os.path.exists(path):
            return path
    return shutil.which("ISCC") or ""


def main() -> int:
    step("Iconos")
    run([sys.executable, os.path.join("tools", "make_icon.py")])

    step("Ejecutable (PyInstaller)")
    # Limpiar dist evita arrastrar archivos de compilaciones anteriores.
    if os.path.isdir(DIST):
        shutil.rmtree(DIST, ignore_errors=True)
    run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
         "hiperpegado.spec"])

    exe = os.path.join(DIST, "Hiperpegado.exe")
    if not os.path.exists(exe):
        sys.exit(f"\nNo se genero {exe}")
    print(f"\n  Listo: {exe}")

    if "--no-installer" in sys.argv:
        return 0

    step("Instalador (Inno Setup)")
    iscc = find_iscc()
    if not iscc:
        print("  Inno Setup 6 no esta instalado; se omite el instalador.")
        print("  Instalalo con:  winget install JRSoftware.InnoSetup")
        print(f"  El ejecutable de {DIST} ya es utilizable tal cual.")
        return 0

    run([iscc, ISS])
    output = os.path.join(ROOT, "installer", "Output")
    print(f"\n  Instalador en: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
