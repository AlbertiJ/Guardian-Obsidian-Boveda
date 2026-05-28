---
tags:
  - creatividad
  - humano
  - programacion
---
# Diario de Incidentes - Guardián de Obsidian v2.2

> Registro de problemas encontrados y soluciones implementadas durante la mejora del sistema Guardián.

---

## 1. Ruta Incorrecta en config.json (CRÍTICO)

**Fecha:** 2026-05-28  
**Severidad:** Alta  
**Sistema:** Windows

### Problema
El script reportaba "0 archivos .md inspeccionados" al ejecutar cualquier opción del menú.

### Diagnóstico
El archivo `config.json` contenía una ruta de Linux:
```json
"vault_path": "/home/albertij/Bovedamobil01/Mobil01"
```

Esta ruta no existe en Windows, por lo que el script buscaba en el lugar equivocado.

### Solución
Actualicé manualmente `config.json` con la ruta correcta de Windows:
```json
"vault_path": "C:\\Users\\juan\\home\\albertij\\Bovedamobil01\\Mobil01"
```

### Prevención
Implementé auto-detección multiplataforma para evitar este problema en el futuro.

---

## 2. Incompatibilidad Multiplataforma (Bóveda Especular)

**Fecha:** 2026-05-28  
**Severidad:** Alta  
**Sistemas:** Windows ↔ Linux  

### Problema
La bóveda está sincronizada entre Windows y Linux mediante espejo. Al ejecutar el script en Linux, la ruta Windows del `config.json` no existía, causando falla total.

### Diagnóstico
El sistema no detectaba automáticamente que estaba corriendo en Linux ni adaptaba la ruta.

### Solución
Implementé la función `detectar_entorno_y_ruta()` que:
1. Lee/crea `.guardian_env` con rutas por plataforma
2. Detecta el SO actual (`platform.system()`)
3. Guarda y recupera rutas específicas para cada sistema

### Prevención
El archivo `.guardian_env` ahora almacena:
```json
{
    "windows_path": "C:\\...",
    "linux_path": "/home/..."
}
```

---

## 3. Auto-Detección de Bóveda (Fallback)

**Fecha:** 2026-05-28  
**Severidad:** Media  
**Sistema:** Linux

### Problema
Cuando la ruta del `config.json` no existía, el script no encontraba la bóveda automáticamente.

### Diagnóstico
No había lógica de fallback para buscar la bóveda en el directorio actual.

### Solución
Agregué búsqueda automática en secuencia:
1. `Mobil01` (caso más común)
2. `Bovedamobil01`
3. `vault`, `obsidian`
4. Directorio del script como último recurso

Si encuentra archivos `.md` o carpeta `.obsidian`, lo usa como ruta activa.

### Prevención
El script ahora funciona incluso si `config.json` tiene rutas obsoletas.

---

## 4. Codificación Unicode en Windows PowerShell

**Fecha:** 2026-05-28  
**Severidad:** Media  
**Sistema:** Windows

### Problema
Al ejecutar modo Dry-Run, el script fallaba con:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u25cb'
```

Los caracteres especiales (→, ○) no se muestran en la terminal Windows (cp1252).

### Solución
Reemplacé símbolos Unicode por equivalentes ASCII:
- `→` → `[>]`
- `○` → `[=]`

### Prevención
Todo el output usa caracteres ASCII estándar para compatibilidad cross-platform.

---

## 5. Output Buffer en Linux (Dry-Run no visible)

**Fecha:** 2026-05-28  
**Severidad:** Media  
**Sistema:** Linux (bash)

### Problema
En Linux, el modo Dry-Run no mostraba el progreso archivo por archivo, solo el resumen final.

### Diagnóstico
El output de Python estaba siendo bufferizado por la tubería (pipe).

### Solución
Agregué `flush=True` a todos los `print()` relevantes:
```python
print(f"    [DRY-RUN] [>] {arc} | Seria modificado", flush=True)
```

### Prevención
Ahora el output se muestra inmediatamente en cualquier terminal (bash, zsh, PowerShell).

---

## 6. Warnings de [[Google]] API en Linux

**Fecha:** 2026-05-28  
**Severidad:** Baja  
**Sistema:** Linux

### Problema
Al ejecutar el script, aparecía un warning molesto:
```
FutureWarning: You are using a Python version (3.10.12) which Google will stop supporting...
```

### Solución
Agregué al inicio del script:
```python
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
```

### Prevención
El output ahora está limpio, sin mensajes de advertencia.

---

## Resumen de Cambios

| Incidente | Causa Raíz | Solución Implementada |
|-----------|------------|----------------------|
| 0 archivos encontrados | Ruta Linux en Windows | Corrección de config.json + auto-detección |
| Falla en Linux | Rutas no adaptables | `.guardian_env` por plataforma |
| Bóveda no detectada | Sin fallback | Búsqueda automática en directorio actual |
| Caracteres Unicode rotos | cp1252 no soporta símbolos | Reemplazo por equivalentes ASCII |
| Output no visible | Buffer de pipe | `flush=True` en todos los prints |
| Warnings molestos | [[Google]] API | `warnings.filterwarnings()` |

---

## Lecciones Aprendidas

1. **Nunca asumir rutas fijas** en sistemas multiplataforma
2. **Siempre verificar existencia de rutas** antes de usarlas
3. **Usar ASCII para output** cuando se requiere compatibilidad cross-platform
4. **Forzar flush en print** cuando hay tuberías o salida en tiempo real
5. **Silenciar warnings de terceros** que no son relevantes para el usuario

---

*Documento generado: 2026-05-28*  
*Versión del sistema: 2.2*  
*Herramientas: Python 3.10+, Mavis AI Assistant*