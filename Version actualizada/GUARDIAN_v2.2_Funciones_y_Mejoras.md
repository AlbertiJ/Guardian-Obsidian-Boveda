---
tags:
  - creatividad
  - humano
  - programacion
  - seguridad
---
# Guardián de Obsidian - Documentación Técnica v2.2

> Sistema de monitoreo y clasificación automática para bóvedas Obsidian sincronizadas entre Windows y Linux.

---

## Funciones Principales

### 1. Clasificación Automática de Notas
Analiza el contenido de archivos `.md` y les asigna etiquetas (`tags`) basándose en palabras clave configurables en `Configuracion-Guardian.md`.

**Categorías predefinidas:**
- `programacion` - python, bash, script, api, code
- `seguridad` - vpn, forense, proxy, credentials
- Y todas las categorías que definas en la configuración

### 2. Interconexión Cruzada de Notas
Genera enlaces `[[wiki-links]]` automáticamente entre notas que comparten títulos similares. Esto enriquece el grafo de Obsidian sin intervención manual.

### 3. Historial de Cambios
Registra todas las modificaciones en `Historial/Historial-de-Boveda.md` con:
- Fecha y hora
- Tipo de evento
- Archivo modificado
- Tags asignados

### 4. Monitoreo en Tiempo Real
- **Polling Loop**: Escanea periódicamente cambios en archivos
- **Watchdog** (opcional): Detecta eventos del sistema de archivos
- Funciona 24x7 en segundo plano como demonio

---

## Menú de Opciones

```
1) Arrancar Guardián Oculto
   - Ejecuta escaneo inicial
   - Activa modo demonio en segundo plano
   
2) Detener Guardián por Completo
   - Limpia procesos de la memoria
   
3) Solo Escaneo Inmediato
   - Escanea todos los archivos una vez
   - No activa demonio
   
4) Simular Escaneo (Dry-Run)
   - Muestra qué archivos serían modificados
   - No escribe nada en disco
```

---

## Mejoras Implementadas v2.2

### Multiplataforma Automática
El script detecta automáticamente el sistema operativo y gestiona rutas distintas para Windows y Linux mediante el archivo `.guardian_env`.

```
Windows: C:\Users\...\Bovedamobil01\Mobil01
Linux:   /home/.../Bovedamobil01/Mobil01
```

### Auto-Detección de Bóveda
Si la ruta configurada no existe, el script busca automáticamente:
1. Subcarpeta `Mobil01` en el directorio actual
2. Subcarpeta `Bovedamobil01`
3. Otras variantes comunes
4. Utiliza el directorio del script como último recurso

### Modo Dry-Run (Simulación)
Permite probar el escaneo sin modificar ningún archivo:
- Muestra cada archivo que sería procesado
- Indica si tendría cambios o no
- Ideal para verificar configuración antes de aplicar

### Backups Automáticos
- Crea `.bak` de `Historial-de-Boveda.md` antes de escribir
- Si falla la escritura, restaura el backup automáticamente

### Salida en Tiempo Real
Todos los mensajes usan `flush=True` para garantir visualización inmediata en cualquier terminal (bash, PowerShell, etc.)

### Silenciado de Warnings
Elimina advertencias de versiones deprecated en bibliotecas de [[Google]] API.

---

## Requisitos

```bash
# Python 3.10+ (3.11 recomendado)
python3 --version

# Dependencias opcionales (instalar con pip):
# - paramiko (para SFTP)
# - google-api-python-client (para Google Drive)
# - watchdog (para monitoreo de eventos)
```

---

## Sincronización entre Plataformas

El script está diseñado para funcionar en una bóveda sincronizada:

1. **Windows**: Editar y ejecutar normalmente
2. **Linux**: El script detecta automáticamente la ruta correcta
3. **Historial**: Se mantiene unificado entre plataformas
4. **Configuración**: Compartida, con guardado de rutas por plataforma

---

## Notas de Configuración

| Archivo | Función |
|---------|---------|
| `config.json` | Ruta de la bóveda (se actualiza automáticamente) |
| `.guardian_env` | Rutas específicas por plataforma |
| `registro_clasificaciones.json` | Log completo de auditorías |
| `Configuracion-Guardian.md` | Palabras clave por categoría |
| `Historial/Historial-de-Boveda.md` | Registro visual de cambios |