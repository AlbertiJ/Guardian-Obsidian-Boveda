---
tags:
  - creatividad
  - humano
  - programacion
---
# 🛡️ Guardián de Obsidian (Versión 2.0 - Arquitectura Unificada)

El **Guardián de Obsidian** es un motor híbrido de orquestación, análisis semántico e interconexionado automatizado diseñado para operar en segundo plano sobre bóvedas de Obsidian. Esta versión V2.0 unifica el antiguo cargador y el script principal en un único demonio autocontenido de alta eficiencia (0% CPU en reposo) y añade una interfaz de control interactiva analizable directamente desde las propiedades nativas de Obsidian.

## 🚀 Características Clave (Evolución V2.0)
*   **Orquestador Autocontenido:** Se eliminó la necesidad de un script lanzador externo. El archivo `guardian_core.py` gestiona su propio ciclo de vida (Arranque invisible, clonación en RAM y detención atómica).
*   **Interfaz Interactiva In-Note:** Control total del historial mediante el Frontmatter (YAML) de Obsidian sin necesidad de complementos externos pesados.
*   **Análisis No Destructivo:** Parser YAML defensivo que lee, procesa y realiza una Unión de Conjuntos (`Set Union`) matemática. Las etiquetas manuales previas del usuario jamás se sobrescriben.
*   **Motor Inmune a Colisiones:** Sustitución de expresiones regulares por búsquedas posicionales indexadas fijas (`.find()`), eludiendo los bloqueos de descriptores de archivos nativos de Windows (*File System Locking*).

---

## 🗂️ Arquitectura Estructural de la Bóveda

Para que el Guardián opere de forma simbiótica, la raíz del directorio debe reflejar los siguientes componentes estructurales (los archivos marcados con 🔒 deben ser incluidos en el `.gitignore` local para proteger tu privacidad):

```text
📂 [Carpeta_Raiz_Sistema]/
├── 📄 guardian_core.py             # Script único unificado (Core del sistema)
├── 🔒 config.json                  # [LOCAL - PRIVADO] Contiene la ruta absoluta física hacia la bóveda
├── 🔒 registro_clasificaciones.json # [LOCAL - PRIVADO] Base de datos relacional de logs en formato JSON
└── 📂 MiBovedaObsidian/             # Raíz física indexada y reconocida por Obsidian
    ├── 📄 00-Indice-General.md      # MOC protegido contra bucles infinitos de enlaces
    ├── 📄 Configuracion-Guardian.md    # Reglas semánticas planas del usuario (Tags/Keywords)
    └── 📂 Historial/
        └── 📄 Historial-de-Boveda.md # Interfaz dinámica interactiva (Logs visuales renderizados)
```

---

## ⚙️ Especificación de la Interfaz Interactiva (`Historial-de-Boveda.md`)

El comportamiento del script se altera modificando los metadatos superiores del archivo de logs. El motor lee de forma síncrona estos parámetros físicos antes de renderizar la tabla:

```yaml
---
limite_resultados: 20          # Límites duros de filas: 10, 20, 30, 40, 50 o "todo"
filtro_fecha: "2026-05"        # Filtrado analítico por Año-Mes (Formato: AAAA-MM)
rango_desde: "2026-05-01"      # Búsqueda segmentada por rango de inicio
rango_hasta: "2026-05-15"      # Búsqueda segmentada por rango de fin
criterio_orden: "modificacion" # Criterio de ordenamiento: "modificacion" o "creacion"
solicitar_exportacion: false   # Switch binario. Cambiar a true vuelca un JSON abajo
---
```

### ⚓ Anclas Invisibles Obligatorias
El script utiliza marcadores de comentarios HTML para delimitar las zonas de inyección sin romper el búfer de edición de Obsidian ni alterar la posición del cursor del usuario:
*   `<!-- START_GUARDIAN_RENDER -->` y `<!-- END_GUARDIAN_RENDER -->` (Zona de la tabla de cambios).
*   `<!-- START_GUARDIAN_JSON -->` y `<!-- END_GUARDIAN_JSON -->` (Zona del volcado de base de datos en JSON).

---

## 🖥️ Ciclo de Operación y Comandos

El script interactúa de forma híbrida mediante el paso de argumentos por consola (Modo Demonio) o interfaz textual CLI:

### 🎮 Interfaz Textual (CLI)
Al ejecutar `python guardian_core.py` sin argumentos, se despliega el menú central:
1.  **Arrancar Guardián Oculto:** Realiza un escaneo total de primer lanzamiento e inicializa la persistencia invisible en la memoria RAM.
2.  **Detener Guardián por Completo:** Ejecuta una limpieza nativa de procesos (`Get-CimInstance` en Windows / `pgrep` en Unix) liberando la memoria al instante.
3.  **Solo Escaneo Inmediato:** Inspección atómica en un único ciclo informando métricas vivas de archivos procesados y modificados en terminal.

### 🥷 Modo Servicio (Segundo Plano)
*   **Levantar Escucha Pasiva:** `python guardian_core.py --serve` (Ejecutado por el automatizador).
*   **Apagar de Memoria:** `python guardian_core.py stop`

---

## 🪟 Automatización Nativa en Windows (Sin privilegios de Admin)

Para garantizar que el Guardián se despliegue de forma 100% invisible (sin consolas CMD emergentes) al encender el sistema informático, se inyecta un script puente de automatización visual en la carpeta de inicio del perfil de usuario mediante el Símbolo del Sistema (CMD).

*Nota: Reemplaza `C:\Ruta\A\Tu\Boveda` por la ubicación real de tu script:*

```cmd
echo CreateObject("Wscript.Shell").Run "pythonw.exe ""C:\Ruta\A\Tu\Boveda\guardian_core.py"" --serve", 0, False > "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\LanzarGuardian.vbs"
```

### 🔬 Ventajas del Puente VBScript:
1.  Invoca a `pythonw.exe` (Binario oculto nativo de Python).
2.  El parámetro `0` fuerza la invisibilidad absoluta de la ventana.
3.  Al alojarse en `%APPDATA%`, **no requiere elevación de privilegios de Administrador** de Windows, lo que mitiga errores de acceso denegado (`HRESULT 0x80070005`).
---
tags:
  - general
---
