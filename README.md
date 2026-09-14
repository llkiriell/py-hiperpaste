<p align="center">
  <img src="assets/icon.png" alt="Hiperpaste" width="128">
</p>

<h1 align="center">Hiperpaste</h1>

<p align="center">
  Pega el contenido del portapapeles <strong>como archivo</strong> desde el menú
  contextual del Explorador de Windows.
</p>

<p align="center">
  <img alt="Versión" src="https://img.shields.io/badge/version-1.1.1-blue">
  <img alt="Plataforma" src="https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-blue">
  <img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-blue">
  <img alt="Licencia" src="https://img.shields.io/badge/license-MIT-green">
</p>

---

Copias un texto o una captura, haces clic derecho dentro de una carpeta, eliges
**Hiperpaste** y el archivo aparece ahí — sin abrir un editor, guardar y ponerle
nombre a mano.

- **Texto** → `.txt` o `.md`
- **Imagen** → `.png` o `.jpg`
- Nombre automático con fecha y hora primero, para que ordene cronológicamente:
  `2026-08-26_14-30-05_Hiperpaste.png`

Además:

- **Atajo de teclado** (`Ctrl+Alt+H` por defecto) para pegar en la carpeta
  abierta sin pasar por el menú.
- **Pegar sin formato** en cualquier aplicación con `Ctrl+Alt+Shift+V`: pega
  el texto del portapapeles limpio de formato (HTML, RTF, enlaces, metadatos).

Incluye icono en la bandeja del sistema con activación rápida, ventana de
configuración y soporte de idiomas (español e inglés, ampliable).

---

## Instalación

Ejecuta `HiperpasteSetup-1.1.1.exe`. Si ya tienes una versión anterior, se
instala encima conservando tu configuración. El asistente pregunta si instalar **solo
para ti** (sin permisos de administrador) o **para todo el equipo**.

Compatible con Windows 10 y Windows 11 (64 bits). No requiere tener Python
instalado.

> **En Windows 11** la opción aparece dentro de **«Mostrar más opciones»** del
> menú contextual, o directamente pulsando **Mayús + clic derecho**. Windows 11
> reserva su menú corto a las extensiones empaquetadas en MSIX, algo fuera del
> alcance de una aplicación de este tipo.

### ¿Venías de Hiperpegado?

La aplicación se llamaba **Hiperpegado** hasta la versión 1.0.0. Al arrancar por
primera vez, Hiperpaste adopta tus ajustes anteriores y retira la entrada vieja
del menú contextual, así que no verás la opción duplicada. Lo único que queda a
mano es **desinstalar Hiperpegado** desde *Añadir o quitar programas*.

## Uso

1. Copia un texto o una imagen (`Ctrl+C`, `Impr Pant`, la Herramienta de
   Recortes…).
2. Clic derecho **en el espacio vacío** de la carpeta donde lo quieres.
3. **Hiperpaste**.

El archivo se crea al instante. Si ya existe uno con ese nombre se añade un
sufijo ` (1)`, ` (2)`… igual que hace el propio Explorador.

### Atajos de teclado

Funcionan en todo Windows mientras el icono de Hiperpaste esté en la bandeja, y
se cambian desde la ventana de configuración.

| Atajo por defecto | Acción |
|---|---|
| `Ctrl+Alt+H` | Pega con Hiperpaste en la carpeta de la ventana del Explorador activa (la pestaña visible) o en el escritorio |
| `Ctrl+Alt+Shift+V` | Pegar sin formato en la aplicación activa |

Al pulsar el botón de un atajo se abre un diálogo que captura la combinación:
debe incluir `Ctrl` o `Alt`, avisa si otra aplicación ya la usa o si está
asignada a la otra acción, y permite dejar la acción **sin atajo** o
**restablecer** el valor por defecto. Con Hiperpaste desactivado, los atajos se
liberan y llegan a la aplicación activa con normalidad.

### Pegar sin formato

Desde Word, el navegador o cualquier otra aplicación, pulsa `Ctrl+Alt+Shift+V`.
No crea ningún archivo: deja en el portapapeles solo el texto Unicode
—descartando HTML, RTF, enlaces y metadatos— y hace un `Ctrl+V` normal en la
ventana activa. El portapapeles queda en texto plano, así que los siguientes
`Ctrl+V` también pegan sin formato.

## Configuración

Clic derecho en el icono de la bandeja:

| Opción | Qué hace |
|---|---|
| **Activado** | Activa o desactiva el pegado. Desactivado, la opción del menú sigue visible pero avisa y no escribe nada |
| **Configuración…** | Abre la ventana de ajustes |
| **Iniciar con Windows** | Arranca la aplicación al iniciar sesión |
| **Buscar actualizaciones…** | Comprueba si hay una versión nueva publicada en GitHub |
| **Acerca de Hiperpaste** | Nombre, versión, licencia y enlace al repositorio |
| **Salir** | Cierra la aplicación |

En la ventana de configuración:

- **Idioma** de la interfaz.
- **Formato** de texto (`.txt` / `.md`) y de imagen (`.png` / `.jpg`).
- **Calidad JPG**, solo cuando el formato de imagen es `.jpg`.
- **Preguntar el nombre al pegar**, con interruptores **independientes** para
  texto y para imagen: puedes pedir el nombre solo para las imágenes y dejar el
  texto automático, o al revés.
- **Sufijo del nombre**, la parte fija que sigue a la fecha.
- **Iniciar con Windows** y **Hiperpaste activado**.
- **Atajos de teclado** para pegar con Hiperpaste y para pegar sin formato.

La configuración se guarda en `%APPDATA%\Hiperpaste\config.json`.

## Actualizaciones

> **Deshabilitado por ahora.** Hiperpaste todavía no está publicado en GitHub,
> así que la opción se muestra en gris y no hace ninguna petición de red. Para
> activarla al publicar la primera *release*, en `hiperpaste/updates.py`: pon
> `ENABLED = True` y sustituye `OWNER` en `GITHUB_REPO` por el usuario real.

Una vez activada, compara la versión instalada con la etiqueta de la última
*release* publicada y, si hay una más nueva, ofrece el enlace de descarga. No
descarga ni instala nada por su cuenta.

## Idiomas

Hiperpaste viene en **español** (por defecto) e **inglés**, y se cambia desde la
ventana de configuración.

### Añadir un idioma

No hace falta recompilar ni saber programar:

1. Copia `locales/_plantilla.json` y ponle de nombre el código
   [ISO 639-1](https://es.wikipedia.org/wiki/ISO_639-1) del idioma: `fr.json`,
   `de.json`, `pt.json`…
2. Déjalo en `%APPDATA%\Hiperpaste\locales\` (crea la carpeta si no existe).
3. Rellena `__meta__` y traduce el valor de cada clave, **sin tocar las claves**.
   Los textos entre llaves como `{app}` o `{version}` son marcadores que la
   aplicación sustituye: consérvalos, aunque puedes reordenarlos.
4. Abre la ventana de configuración: el idioma nuevo ya aparece en la lista.

Las claves que dejes sin traducir se muestran en español, así que puedes empezar
por las que más se ven. Un archivo con un error de sintaxis se ignora sin
impedir que la aplicación arranque.

Los archivos de esa carpeta tienen prioridad sobre los que trae la aplicación,
de modo que también sirven para corregir una traducción existente. Si quieres
que tu idioma se distribuya con Hiperpaste, colócalo en `locales/` del
repositorio y abre una *pull request*.

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
| `Hiperpaste.exe` · `--tray` | Inicia el icono de bandeja (instancia única) |
| `Hiperpaste.exe --paste RUTA` | Pega el portapapeles en `RUTA`. Es lo que invoca el menú contextual |
| `Hiperpaste.exe --paste-plain` | Pega sin formato en la ventana activa (lo mismo que su atajo) |
| `Hiperpaste.exe --config` | Abre la ventana de configuración |
| `Hiperpaste.exe --about` | Abre la ventana Acerca de |
| `Hiperpaste.exe --register` / `--unregister` | Da de alta o de baja la opción del menú |

### Compilar

```bash
python build.py                  # iconos + ejecutable + instalador
python build.py --no-installer   # se detiene tras el ejecutable
```

Requiere [Inno Setup 6](https://jrsoftware.org/isinfo.php) para el instalador
(`winget install JRSoftware.InnoSetup`). Sin él, `build.py` genera igualmente
el ejecutable en `dist\Hiperpaste\` y avisa.

### Estructura

```
hiperpaste/
  cli.py          despacho de argumentos
  config.py       configuración en JSON
  i18n.py         carga de idiomas y traducción de textos
  clipboard.py    lectura y limpieza del portapapeles (PNG, DIB, texto, HTML)
  paste.py        nombres, colisiones y escritura de los archivos
  plainpaste.py   pegar sin formato en la ventana activa
  keycombo.py     combinaciones de teclas: validación y texto visible
  hotkeys.py      atajos globales atendidos desde la bandeja
  explorer.py     carpeta abierta en la ventana activa del Explorador
  registry.py     menús contextuales y arranque con Windows (todo en HKCU)
  migrate.py      traspaso desde la instalación previa de Hiperpegado
  updates.py      comprobación de versiones contra las releases de GitHub
  tray.py         icono de bandeja
  ui/             ventanas de configuración, Acerca de, nombre de archivo y
                  captura de atajos
locales/          idiomas (es, en) y plantilla para añadir más
tools/make_icon.py   genera assets/icon.ico, icon.png e icon_off.ico
installer/           script de Inno Setup
```

Para usar un icono propio, sustituye `assets/icon.ico`, `assets/icon.png` y
`assets/icon_off.ico` y vuelve a compilar. `build.py` solo los regenera si los
borras; para forzarlo, `python tools/make_icon.py --force`.

### Detalles de implementación

- El proceso de pegado **no depende de la bandeja**: lee la configuración por su
  cuenta, así que el menú contextual sigue funcionando aunque hayas cerrado la
  aplicación.
- El menú se registra con el token `%V` bajo `Directory\Background\shell`, que es
  el que entrega la carpeta abierta (`%1` no funciona en esa clave).
- La bandeja **repara** la entrada del registro en cada arranque, de modo que
  sobrevive a mover la aplicación de sitio y, en instalaciones para todo el
  equipo, se da de alta para cada usuario la primera vez que la ejecuta.
- El texto se guarda en UTF-8 **con BOM** y saltos CRLF: sin ello, el Bloc de
  notas de Windows 10 muestra los acentos corruptos y el texto en una sola línea.
- Al convertir a JPG una imagen con transparencia, se compone sobre fondo blanco
  antes de convertir (JPEG no admite canal alfa).
- Las ventanas se abren como **procesos aparte**: `pystray` ocupa el hilo
  principal con su bucle de eventos y tkinter exige ese mismo hilo.
- El español es el idioma fuente y actúa de respaldo: una traducción incompleta
  degrada clave a clave, nunca deja la interfaz en blanco.
- Los atajos se registran con `RegisterHotKey` en un hilo propio de la bandeja,
  que relee la configuración cuando cambia en disco: no hace falta reiniciar
  tras guardar. Mientras el diálogo de captura está abierto, la bandeja suelta
  sus atajos (señal con un mutex con nombre); si no, Windows se los entregaría a
  ella y no se podrían reasignar.
- Pegar sin formato espera a que se suelten `Ctrl`, `Alt` y `Shift` antes de
  simular `Ctrl+V`: con ellos pulsados llegaría `Ctrl+Alt+Shift+V` y volvería a
  disparar el atajo.
- `registry.py` conserva, **oculto**, un menú en cascada **Hipertools**
  (`SubCommands` vacío y subclave `shell`) para futuras herramientas del clic
  derecho: se activa con `TOOLS_MENU_VISIBLE` y añadiendo opciones a
  `_TOOLS_ITEMS`. Mientras está oculto, la bandeja retira al arrancar las claves
  que dejó la versión 1.1.0.

### Limitación conocida

En una instalación **para todo el equipo**, el desinstalador se ejecuta como
administrador y limpia la clave del menú contextual de ese usuario, pero no la
de otros usuarios del equipo que hayan usado la aplicación. Es un residuo
inofensivo: una clave que apunta a un ejecutable inexistente, que Windows
ignora. Cada usuario afectado puede borrarla con:

```
reg delete "HKCU\Software\Classes\Directory\Background\shell\Hiperpaste" /f
```

---

## Licencia

[MIT](LICENSE)
