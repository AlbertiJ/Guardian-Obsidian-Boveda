#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from pathlib import Path

# --- CONFIGURACIÓN AUTOMÁTICA DE RUTAS ---
DIRECTORIO_ACTUAL = Path(__file__).parent.resolve()
SCRIPT_PRINCIPAL = DIRECTORIO_ACTUAL / "guardian_vault_final.py"
CONFIG_FILE = DIRECTORIO_ACTUAL / "config.json"

# Detectar la bóveda al lado del script o usar una ruta por defecto portable
BOVEDA_SUGERIDA = DIRECTORIO_ACTUAL / "Mobil01"

def limpiar_procesos_anteriores():
    """Busca y elimina instancias previas del guardián para evitar duplicados en memoria."""
    print("[*] Limpiando procesos fantasmas en segundo plano...")
    if sys.platform == "win32":
        # Mata procesos de python que estén ejecutando nuestro script específico
        subprocess.run('wmic process where "commandline like \'%guardian_vault_final.py%\'" delete', 
                       shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        # Comando nativo para Linux/macOS
        subprocess.run(["pkill", "-f", "guardian_vault_final.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def gestionar_configuracion():
    """Garantiza la existencia del config.json para evitar bloqueos por peticiones de teclado (input)."""
    if not CONFIG_FILE.exists():
        print(f"[!] Archivo config.json no detectado. Generando plantilla automática...")
        ruta_boveda = input(f"[?] Introduce la ruta de tu bóveda [Por defecto: {BOVEDA_SUGERIDA}]: ").strip()
        if not ruta_boveda:
            ruta_boveda = str(BOVEDA_SUGERIDA)
        
        config_data = {
            "vault_path": os.path.normpath(ruta_boveda.replace('"', '').replace("'", "")),
            "modo": "2"
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        print("[+] Archivo config.json creado correctamente.")

def lanzar_oculto():
    """Despliega el script principal en segundo plano verdadero según el Sistema Operativo."""
    if not SCRIPT_PRINCIPAL.exists():
        print(f"[-] Error Crítico: No se encuentra {SCRIPT_PRINCIPAL.name} en este directorio.")
        sys.exit(1)

    limpiar_procesos_anteriores()
    gestionar_configuracion()

    print(f"[+] Lanzando {SCRIPT_PRINCIPAL.name} en segundo plano invisible...")
    
    if sys.platform == "win32":
        # Ejecución oculta nativa en Windows usando pythonw (elimina la ventana negra de CMD por completo)
        # Si pythonw no está mapeado, se usa el puente invisible de PowerShell de forma segura
        comando_ps = f"Start-Process python -ArgumentList '{SCRIPT_PRINCIPAL}' -WindowStyle Hidden"
        subprocess.Popen(["powershell", "-Command", comando_ps], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        # Ejecución desacoplada (Modo Demonio) nativa en Linux/Bash
        with open(os.devnull, 'r') as devnull:
            subprocess.Popen([sys.executable, str(SCRIPT_PRINCIPAL)], 
                             stdin=devnull, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)

    print("[🚀] ¡Guardián operativo y controlando todo desde las sombras!")

def detener_guardian():
    """Apaga el guardián de inmediato."""
    limpiar_procesos_anteriores()
    print("[🛑] El Guardián ha sido desactivado y removido de la memoria.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "stop":
        detener_guardian()
    else:
        print("====================================================")
        print("          AUTOMATIZADOR DE ENTORNO GUARDIÁN         ")
        print("====================================================")
        print("1) Arrancar Guardián Oculto de forma Invisible")
        print("2) Detener y Apagar Guardián de fondo")
        op = input("Selecciona [1-2]: ").strip()
        
        if op == "1": lanzar_oculto()
        elif op == "2": detener_guardian()
        else: print("[-] Opción inválida.")
