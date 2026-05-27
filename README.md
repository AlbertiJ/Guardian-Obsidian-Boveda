---
tags:
  - creatividad
  - humano
  - programacion
  - seguridad
---
💿 Guardian Vault Pro — Multiplatform Obsidian Semantic Indexer & Custodian

`Guardian Vault Pro` es un demonio (_daemon_) asíncrono multiplataforma de bajo consumo diseñado para automatizar la interconexión de conceptos cruzados (**WikiLinks**) y la inyección de propiedades de metadatos (**YAML Tags**) de forma nativa dentro de bóvedas de Obsidian. Es compatible con infraestructuras locales y arquitecturas distribuidas en la nube ([[Google]] Drive API / Servidores remotos Linux vía SSH/SFTP).

💡 Idea Base y Origen del Proyecto

El proyecto nació de una necesidad real del creador y diseñador de la infraestructura: **automatizar la organización semántica y el etiquetado de bases de conocimiento masivas en Obsidian sin perder el control de los archivos**.

> 👨‍💻 **Nota del Autor:** Este software no fue estructurado por un programador de carrera, sino por un implementador enfocado en resolver una necesidad operativa real. La suite actual es el resultado de un riguroso proceso de ingeniería inversa, pruebas continuas en entornos de producción, validación manual de logs de control y refactorización paso a paso para mitigar riesgos de corrupción de datos.

📈 Evolución del Desarrollo

1. **Fase 1 (Interfaz y Segmentación)**: Prototipo inicial enfocado en la absorción y tratamiento de streams de audio (Web UI + Flask Backend) para indexar fragmentos multimedia.
2. **Fase 2 (Custodia y Normalización)**: Migración hacia el análisis de texto plano en Obsidian, estructurando un motor interactivo de consola para inyectar cabeceras YAML y auditoría mediante JSON local.
3. **Fase 3 (Blindaje e Interconexión Cruzada)**: Implementación de medidas _Hardened_ de seguridad forense (escritura atómica con `tempfile`, límites de tamaño por DoS y evasión de bucles en la nube). Se recuperó e inyectó el motor _WikiLinker_ para conectar conceptos automáticamente.
4. **Fase 4 (Desacoplamiento y Cero Consumo)**: Separación total de las palabras clave fijas en el código mediante un lector Markdown MOC. Integración de la API de eventos del Kernel para reducir el impacto de procesamiento a cero absoluto.

💎 Características Principales

- **Consumo Pasivo (0% CPU)**: En lugar de realizar barridos continuos que desgastan el disco, la suite implementa la librería `watchdog`, acoplándose directamente a los eventos nativos del sistema operativo (`inotify` en Linux y `ReadDirectoryChangesW` en Windows). El script permanece inactivo y solo se activa en milisegundos cuando guardas una nota.
- **Escritura Atómica Anti-Corrupción**: El guardado se procesa mediante buffers temporales aislados. Si ocurre un corte de energía o una colisión de sincronización en la nube ([[Google]] Drive, Nextcloud, OneDrive), tus archivos originales jamás sufrirán pérdida de bytes.
- **Validador Anti-Broken Links**: El motor de interconexión analiza tu bóveda y solo genera enlaces azules (`[[concepto]]`) si el archivo de destino existe de verdad en el almacenamiento, previniendo enlaces fantasma.
- **Lector de Criterios Desacoplado**: Modifica tus etiquetas y palabras clave directamente desde la nota `Configuracion-Guardian.md` dentro de Obsidian. No necesitas tocar el archivo de Python para alterar el comportamiento del clasificador.
- **Auditoría Dual Avanzada**: Genera de forma simultánea un archivo estructurado `registro_clasificaciones.json` para bases de datos y construye una tabla Markdown interactiva en tiempo real dentro de tu bóveda bajo la ruta `Historial/Historial-de-Boveda.md`.

# 🌲 Estructura del Directorio del Proyecto##

La suite se compone de una arquitectura desacoplada, limpia y sin rutas rígidas o absolutas del sistema:
---
📂 guardian-vault-pro/
├── 📄 guardian_vault_final.py     # Motor Core: Clasificador semántico, WikiLinker y Watchdog.
├── 📄 lanzador_guardian.py       # Script de Ocultación, Gestión en segundo plano y Anti-Duplicados.
├── 📄 config.json                # Variables de entorno locales (Ruta de Bóveda y Modos de inicio).
├── 📄 registro_clasificaciones.json # Base de datos local histórica de auditoría (JSON).
└── 📄 README.md                  # Documentación técnica del repositorio.

# 🛠️ Instalación de Dependencias##

Antes de lanzar el ecosistema por primera vez, abre tu terminal (Linux) o PowerShell (Windows) e instala los módulos estándar de monitoreo de sistema y protocolos de red:

pip install watchdog paramiko [[google]]-api-python-client [[google]]-auth-httplib2 [[google]]-auth-oauthlib

---

## 🚀 Guía de Operación Automatizada (Modo Oculto)

Para evitar lidiar con comandos extensos o mantener molestas ventanas negras abiertas en tu barra de tareas, se diseñó el script de ocultación **`lanzador_guardian.py`**. Este automatizador analiza tu sistema operativo, limpia la memoria de procesos duplicados anteriores y despliega el Guardián en segundo plano verdadero de forma invisible.
### 🐧 Operación en Linux
Asegura permisos e inicia el script de forma interactiva o como servicio persistente:
```bash
# Ejecución estándar en consola
python3 guardian_vault_final.py

# Ejecución en segundo plano persistente (Guarda logs)
nohup python3 guardian_vault_final.py > guardian.log 2>&1 &
```

### 🪟 Operación en Windows (PowerShell / CMD)

Abre tu terminal / consola de comandos y ejecuta el script automatizador (como Administrador):
Abre tu consola de PowerShell (como Administrador) y ejecuta:

powershell

```
# Habilitar políticas si Windows restringe scripts externos
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Lanzar el menú oculto de aprovisionamiento
python lanzador_guardian.py
```
- Selecciona la **Opción 1** para arrancar el Guardián de forma invisible (utiliza `pythonw` y puentes de Windows para ocultar el entorno de ejecución).
- Selecciona la **Opción 2** para apagarlo y limpiar la memoria RAM de inmediato.

### 🐧 Operación en Linux (Bash)##

```
bash

# Asignar capacidades de ejecución al automatizador
chmod +x lanzador_guardian.py

# Iniciar el controlador
python3 lanzador_guardian.py

```

🛑 Cómo Detener el Guardián de Fondo

Si iniciaste el software en modo oculto e invisible y necesitas removerlo de la memoria del sistema:

- **Vía Automatizador**: Ejecuta `python lanzador_guardian.py` y selecciona la **Opción 2**.
- **Matar Proceso en Windows (Consola)**: `wmic process where "commandline like '%guardian_vault_final.py%'" delete`.
- **Matar Proceso en Linux (Consola)**: `pkill -f guardian_vault_final.py`.

---
🔮 Futuras Mejoras en el Roadmap

- **Instalador Multiplataforma Nativo**: Empaquetado binario ejecutable en un solo clic (`.exe` para Windows y ejecutable binario autónomo para Linux).
- **Capa Criptográfica de Notas**: Cifrado automático _Zero-Knowledge_ de archivos con información confidencial o credenciales antes de ser empujados a nubes públicas.
- **Dashboard de Analíticas**: Módulo web de lectura de logs para generar mapas visuales de calor sobre el crecimiento semántico de las notas.
---
## 🕒 Casos de Uso y Verificación
1. **Modo Local Inteligente**: Selecciona la Opción 1 al arrancar. El script analizará tu disco rígido automáticamente, mapeará tus bóvedas y te listará un menú numérico para que elijas cuál custodiar.
2. **Auto-Enlazado Dinámico**: Crea una nota con el texto *"Estoy estudiando conceptos de python e iptables"*. Si tienes notas llamadas `python.md` e `iptables.md`, el script las transformará al instante en links navegables sin romper bloques de código ni alterar el frontmatter.
3. **Control Cloud-Safe**: Al conectarse a carpetas de [[Google]] Drive o servidores Linux vía SFTP (con soporte de lectura automática de llaves privadas `id_rsa`), el script previene bucles infinitos de sincronización generados por marcas de tiempo alteradas por las nubes.

---
⚖️ Licencia y Comunidad

Este proyecto es **Open Source** (Software Libre) y está abierto a contribuciones de la comunidad de gestión del conocimiento y ciberseguridad. Siéntete libre de clonarlo, auditar el código atómico y realizar pull requests.
🏷️ Tags & Indexación de Comunidad (GitHub Discovery)

#ObsidianMD #Python #Automation #InformationSecurity #Productivity #FileCarving #DataStructure #Markdown #CloudSync #Systemd #WindowsPowerShell #LinuxTools #Watchdog #WebDAV #GoogleDriveAPI #OpenSource