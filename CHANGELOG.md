# Changelog

Todos los cambios notables en este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/)
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [1.2.0] - 2026-10-17

### Añadido
- **Menú contextual Hipertools > Copiar ruta**: Permite copiar la ruta absoluta de archivos y carpetas directamente desde el menú contextual del Explorador de Windows (`*` y `Directory`).
- **Atajo global de teclado (`Ctrl+Alt+C`)**: Copia la ruta absoluta de los archivos o carpetas seleccionados en la ventana activa del Explorador o en el Escritorio sin necesidad de desplegar el menú contextual.
- **Soporte para múltiples rutas**: Copia una lista de rutas absolutas separadas por saltos de línea cuando se seleccionan múltiples archivos.
- **Configuración de copia múltiple y límites**:
  - Opción para activar o desactivar la copia de múltiples rutas (desactivada por defecto).
  - Límite numérico configurable de archivos permitidos en la copia múltiple (por defecto 50 archivos).
  - Notificaciones en la bandeja y avisos cuando se excede el límite permitido.
- **Nueva sección Hipertools en Ajustes**: Controles dedicados en la ventana de configuración para activar la copia múltiple y definir el límite de archivos.
- **Iconos contextuales**: Icono oficial de Hiperpaste en el menú agrupador Hipertools y en la opción Copiar ruta.
- **Soporte multilingüe**: Traducciones añadidas en español (`es.json`), inglés (`en.json`) y plantilla (`_plantilla.json`).
- **Comprobación de actualizaciones activa**: Habilitada la búsqueda de actualizaciones directamente contra las releases oficiales de GitHub (`llkiriell/py-hiperpaste`) desde la ventana Acerca de y el menú de la bandeja.
- **Despacho CLI**: Nuevo comando `Hiperpaste.exe --copy-path RUTA`.

---

## [1.1.1] - 2026-08-27

### Corregido
- Ocultar el menú Hipertools y retirar la opción Pegar sin formato del Explorador, conservándola exclusivamente mediante su atajo global de teclado.
- Cierre previo de la bandeja antes de instalar una actualización sobre una versión existente.

---

## [1.1.0] - 2026-08-27

### Añadido
- Atajos de teclado globales atendidos desde el proceso de la bandeja.
- Modal interactivo de captura de atajos en la ventana de Ajustes.
- Pegar sin formato (`Ctrl+Alt+Shift+V`).
- Soporte de idiomas (español e inglés) y plantilla para añadir nuevas traducciones.
- Ventana Acerca de y sistema de comprobación de actualizaciones.

---

## [1.0.0] - 2026-08-26

### Añadido
- Versión inicial tras la transición desde Hiperpegado.
- Pegado directo del portapapeles como archivo desde el menú contextual (`.txt`, `.md`, `.png`, `.jpg`).
- Soporte para nombres con marca de tiempo cronológica y diálogo para renombrar.
- Icono en la bandeja del sistema e instalador para Windows 10 y 11.
