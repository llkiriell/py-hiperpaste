# Hiperpegado

Pega el contenido del portapapeles **como archivo** desde el menú contextual del
Explorador de Windows. Copias un texto o una captura, haces clic derecho dentro
de una carpeta, eliges **Hiperpegado** y el archivo aparece ahí — sin abrir un
editor, guardar y ponerle nombre a mano.

- **Texto** → `.txt` o `.md`
- **Imagen** → `.png` o `.jpg`
- Nombre automático con fecha y hora primero, para que ordene cronológicamente:
  `2026-08-26_14-30-05_Hiperpegado.png`

Incluye icono en la bandeja del sistema con activación rápida y una ventana de
configuración.

---

## Instalación

Ejecuta `HiperpegadoSetup-1.0.0.exe`. El asistente pregunta si instalar **solo
para ti** (sin permisos de administrador) o **para todo el equipo**.

Compatible con Windows 10 y Windows 11 (64 bits). No requiere tener Python
instalado.

> **En Windows 11** la opción aparece dentro de **«Mostrar más opciones»** del
> menú contextual, o directamente pulsando **Mayús + clic derecho**. Windows 11
> reserva su menú corto a las extensiones empaquetadas en MSIX, algo fuera del
> alcance de una aplicación de este tipo.

## Uso

1. Copia un texto o una imagen (`Ctrl+C`, `Impr Pant`, la Herramienta de
   Recortes…).
2. Clic derecho **en el espacio vacío** de la carpeta donde lo quieres.
3. **Hiperpegado**.

El archivo se crea al instante. Si ya existe uno con ese nombre se añade un
sufijo ` (1)`, ` (2)`… igual que hace el propio Explorador.

## Configuración

Clic derecho en el icono de la bandeja:

| Opción | Qué hace |
|---|---|
| **Activado** | Activa o desactiva el pegado. Desactivado, la opción del menú sigue visible pero avisa y no escribe nada |
| **Configuración…** | Abre la ventana de ajustes |
| **Iniciar con Windows** | Arranca la aplicación al iniciar sesión |
| **Salir** | Cierra la aplicación |

En la ventana de configuración:

- **Formato** de texto (`.txt` / `.md`) y de imagen (`.png` / `.jpg`).
- **Calidad JPG**, solo cuando el formato de imagen es `.jpg`.
- **Preguntar el nombre al pegar**, con interruptores **independientes** para
  texto y para imagen: puedes pedir el nombre solo para las imágenes y dejar el
  texto automático, o al revés.
- **Sufijo del nombre**, la parte fija que sigue a la fecha.
- **Iniciar con Windows** y **Hiperpegado activado**.

La configuración se guarda en `%APPDATA%\Hiperpegado\config.json`.

---

## Desarrollo

```bash
pip install -r requirements.txt
python main.py --tray        # bandeja (registra la opción del menú al arrancar)
```

Ejecutar desde el código fuente registra el menú contextual apuntando al
`pythonw.exe` del entorno actual, así que la opción funciona igual mientras
desarrollas.

### Línea de comandos

| Comando | Efecto |
|---|---|
| `Hiperpegado.exe` · `--tray` | Inicia el icono de bandeja (instancia única) |
| `Hiperpegado.exe --paste RUTA` | Pega el portapapeles en `RUTA`. Es lo que invoca el menú contextual |
| `Hiperpegado.exe --config` | Abre la ventana de configuración |
| `Hiperpegado.exe --register` / `--unregister` | Da de alta o de baja la opción del menú |

### Compilar

```bash
python build.py                  # iconos + ejecutable + instalador
python build.py --no-installer   # se detiene tras el ejecutable
```

Requiere [Inno Setup 6](https://jrsoftware.org/isinfo.php) para el instalador
(`winget install JRSoftware.InnoSetup`). Sin él, `build.py` genera igualmente
el ejecutable en `dist\Hiperpegado\` y avisa.

### Estructura

```
hiperpegado/
  cli.py          despacho de argumentos
  config.py       configuración en JSON
  clipboard.py    lectura del portapapeles (PNG, DIBv5, DIB, texto, archivos)
  paste.py        nombres, colisiones y escritura de los archivos
  registry.py     menú contextual y arranque con Windows (todo en HKCU)
  tray.py         icono de bandeja
  ui/             ventana de configuración y diálogo de nombre
tools/make_icon.py   genera assets/icon.ico e icon_off.ico
installer/           script de Inno Setup
```

Para usar un icono propio, sustituye `assets/icon.ico` y `assets/icon_off.ico`
y vuelve a compilar (`build.py` solo los regenera si los borras).

### Detalles de implementación

- El proceso de pegado **no depende de la bandeja**: lee la configuración por su
  cuenta, así que el menú contextual sigue funcionando aunque hayas cerrado la
  aplicación.
- El menú se registra con el token `%V` bajo
  `Directory\Background\shell`, que es el que entrega la carpeta abierta (`%1`
  no funciona en esa clave).
- La bandeja **repara** la entrada del registro en cada arranque, de modo que
  sobrevive a mover la aplicación de sitio y, en instalaciones para todo el
  equipo, se da de alta para cada usuario la primera vez que la ejecuta.
- El texto se guarda en UTF-8 **con BOM** y saltos CRLF: sin ello, el Bloc de
  notas de Windows 10 muestra los acentos corruptos y el texto en una sola línea.
- Al convertir a JPG una imagen con transparencia, se compone sobre fondo blanco
  antes de convertir (JPEG no admite canal alfa).
- La ventana de configuración se abre como **proceso aparte**: `pystray` ocupa el
  hilo principal con su bucle de eventos y tkinter exige ese mismo hilo.

### Limitación conocida

En una instalación **para todo el equipo**, el desinstalador se ejecuta como
administrador y limpia la clave del menú contextual de ese usuario, pero no la
de otros usuarios del equipo que hayan usado la aplicación. Es un residuo
inofensivo: una clave que apunta a un ejecutable inexistente, que Windows
ignora. Cada usuario afectado puede borrarla con:

```
reg delete "HKCU\Software\Classes\Directory\Background\shell\Hiperpegado" /f
```
