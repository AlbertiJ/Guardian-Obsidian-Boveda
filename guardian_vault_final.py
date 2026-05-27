#!/usr/bin/env python3
import os
import re
import sys
import time
import json
import tempfile
from pathlib import Path
from datetime import datetime

# --- SOPORTE MULTIPLATAFORMA DE PROTOCOLOS DE RED ---
try:
    import paramiko
except ImportError:
    paramiko = None

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    SCOPES = ['https://googleapis.com']
except ImportError:
    build = None

# --- SOPORTE DE EVENTOS NATIVOS DE BAJO CONSUMO (KERNEL) ---
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False

# --- CONFIGURACIÓN DE SEGURIDAD E INFRAESTRUCTURA ---
LOG_AUDITORIA = "registro_clasificaciones.json"
CONFIG_FILE = "config.json"
CONFIG_NOTA_NAME = "Configuracion-Guardian.md"
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB máximo por nota
MOC_NAME = "00-Indice-General.md"

IGNORAR_CARPETAS = {
    '.obsidian', '.trash', '.git', 'attachments', 'node_modules', 'Historial',
    'Program Files', 'Program Files (x86)', 'Windows', 'AppData', 
    'System Volume Information', 'Recovery', '$Recycle.Bin', 'usr', 
    'bin', 'lib', 'var', 'etc', 'proc', 'sys', 'dev', 'boot', 'home'
}

# Criterios de contingencia por defecto (Si no existe la nota de configuración en Obsidian)
CRITERIOS_DEFAULT = {
    "programacion": ["python", "bash", "script", "iptables", "kernel", "router", "servidor", "network", "code", "frontend", "backend", "api"],
    "seguridad": ["vpn", "forense", "proxy", "tunnel", "killswitch", "ofuscación", "ram", "credentials", "macchanger", "root", "nuclear", "purge"]
}

# --- LECTOR DESACOPLADO DE CRITERIOS (MARKDOWN MOC LOADER) ---
def cargar_criterios_desde_obsidian(vault_path):
    """Busca y parsea la nota Configuracion-Guardian.md para extraer tags y keywords dinámicamente."""
    ruta_config_nota = Path(vault_path) / CONFIG_NOTA_NAME
    if not ruta_config_nota.exists():
        # Si no existe, crea una plantilla automática para el usuario
        try:
            with open(ruta_config_nota, 'w', encoding='utf-8') as f:
                f.write(f"# 🛠️ Configuración del Guardián\n\n")
                f.write("Define aquí tus reglas semánticas usando el formato `tag: keyword1, keyword2`:\n\n")
                f.write("programacion: python, bash, script, iptables, servidor, api, code\n")
                f.write("seguridad: vpn, forense, proxy, killswitch, credentials, root\n")
                f.write("creatividad: diseño, ui, ux, figma, svg, interfaz, layout\n")
                f.write("humano: psicología, filosofía, mente, historia, cultura, sociedad\n")
        except: pass
        return CRITERIOS_DEFAULT

    criterios_dinamicos = {}
    try:
        with open(ruta_config_nota, 'r', encoding='utf-8') as f:
            for linea in f:
                if ":" in linea and not linea.startswith("#") and not linea.startswith(">"):
                    parts = linea.split(":", 1)
                    tag = parts[0].strip().lower()
                    keywords = [k.strip().lower() for k in parts[1].split(",") if k.strip()]
                    if tag and keywords:
                        criterios_dinamicos[tag] = keywords
        return criterios_dinamicos if criterios_dinamicos else CRITERIOS_DEFAULT
    except:
        return CRITERIOS_DEFAULT

def cargar_config_json():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: pass
    return None

# --- MÓDULO DE AUDITORÍA DUAL (JSON + NOTA DE OBSIDIAN) ---
def registrar_log(ruta_nota, tags, vault_path, origen="Local"):
    fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_archivo = os.path.basename(ruta_nota)
    
    registro = {
        "fecha_actualizacion": fecha_str, "archivo": nombre_archivo, 
        "ruta_origen": os.path.normpath(ruta_nota), "entorno_ejecucion": origen, "tags_detectados": tags
    }
    datos = []
    if os.path.exists(LOG_AUDITORIA):
        try:
            with open(LOG_AUDITORIA, 'r', encoding='utf-8') as f: datos = json.load(f)
        except: pass
    datos.append(registro)
    try:
        with open(LOG_AUDITORIA, 'w', encoding='utf-8') as f: json.dump(datos, f, indent=4, ensure_ascii=False)
    except: pass

    if vault_path and os.path.isdir(vault_path):
        carpeta_historial = Path(vault_path) / "Historial"
        carpeta_historial.mkdir(exist_ok=True)
        nota_historial = carpeta_historial / "Historial-de-Boveda.md"
        
        if not nota_historial.exists():
            with open(nota_historial, 'w', encoding='utf-8') as f:
                f.write("# 📜 Historial de Modificaciones de la Bóveda\n\n")
                f.write("> Bienvenido a tu historial de la boveda. Guardia operativo y controlando todo.\n\n")
                f.write("| Fecha y Hora | Archivo | Entorno | Tags Asignados |\n| --- | --- | --- | --- |\n")
        
        with open(nota_historial, 'a', encoding='utf-8') as f:
            tags_str = ", ".join(tags)
            f.write(f"| {fecha_str} | `[[{nombre_archivo.replace('.md', '')}]]` | **{origen}** | `{tags_str}` |\n")

# --- MÓDULO DE AUTO-DESCUBRIMIENTO ---
def descubrir_bovedas_locales():
    print("[*] Ejecutando motor de auto-descubrimiento local...")
    raiz_disco = Path(os.path.abspath(os.sep))
    bovedas_encontradas = []
    try:
        for raiz, dirs, _ in os.walk(raiz_disco):
            dirs[:] = [d for d in dirs if d not in IGNORAR_CARPETAS and not d.startswith('.')]
            if '.obsidian' in dirs:
                bovedas_encontradas.append(Path(raiz))
                dirs.clear() 
    except Exception as e:
        print(f"[!] Aviso en escaneo: {e}")

    if not bovedas_encontradas:
        return os.path.normpath(input("[?] Ingresa la ruta de tu bóveda: ").strip().replace('"', '').replace("'", ""))

    print(f"\n[+] Se encontraron {len(bovedas_encontradas)} bóvedas potenciales:")
    for idx, boveda in enumerate(bovedas_encontradas, 1): print(f"{idx}) {boveda}")
    print(f"{len(bovedas_encontradas) + 1}) Ingresar ruta manualmente...")

    while True:
        try:
            opcion = int(input(f"Selecciona la bóveda [1-{len(bovedas_encontradas)+1}]: ").strip())
            if 1 <= opcion <= len(bovedas_encontradas): return str(bovedas_encontradas[opcion - 1])
            elif opcion == len(bovedas_encontradas) + 1:
                return os.path.normpath(input("[?] Ruta de tu bóveda: ").strip().replace('"', '').replace("'", ""))
        except ValueError: pass

# --- MÓDULO REMOTO (GDRIVE & SFTP) ---
def inicializar_entorno_remoto():
    print("\n[☁️] ENTORNO REMOTO\n1) Google Drive API\n2) SSH / SFTP Linux Server")
    tipo_nube = input("Selecciona [1-2]: ").strip()
    temp_remote_mirror = Path(tempfile.gettempdir()) / "obsidian_remote_mirror"
    temp_remote_mirror.mkdir(exist_ok=True)

    if tipo_nube == "1":
        if build is None: return None
        creds = None
        if os.path.exists('token.json'): creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token: creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token: token.write(creds.to_json())
        service = build('drive', 'v3', credentials=creds)
        folder_id = input("[?] ID Carpeta Drive (Vacío para auto-crear): ").strip()
        if not folder_id:
            folder = service.files().create(body={'name': 'Obsidian_Vault_Cloud', 'mimeType': 'application/vnd.google-apps.folder'}, fields='id').execute()
            folder_id = folder.get('id')
        return {"tipo": "gdrive", "service": service, "folder_id": folder_id, "local_mirror": str(temp_remote_mirror)}

    elif tipo_nube == "2":
        if paramiko is None: return None
        host = input("Host SSH: ").strip()
        user = input("Usuario SSH: ").strip()
        passwd = input("Contraseña (Vacío para usar llave RSA id_rsa): ").strip()
        remote_path = input("Ruta remota de la bóveda: ").strip()
        try:
            transport = paramiko.Transport((host, 22))
            if passwd: transport.connect(username=user, password=passwd)
            else:
                pkey = paramiko.RSAKey.from_private_key_file(os.path.expanduser("~/.ssh/id_rsa"))
                transport.connect(username=user, pkey=pkey)
            sftp = paramiko.SFTPClient.from_transport(transport)
            return {"tipo": "sftp", "sftp": sftp, "remote_path": remote_path, "local_mirror": str(temp_remote_mirror)}
        except Exception as e: print(f"[-] Error SSH: {e}"); return None
    return None

def sincronizar_remoto_a_local(creds):
    mirror = creds["local_mirror"]
    if creds["tipo"] == "gdrive":
        results = creds["service"].files().list(q=f"'{creds['folder_id']}' in parents and mimeType='text/markdown' and trashed=false").execute()
        for file in results.get('files', []):
            with open(os.path.join(mirror, file['name']), 'wb') as f:
                f.write(creds["service"].files().get_media(fileId=file['id']).execute())
    elif creds["tipo"] == "sftp":
        for f_attr in creds["sftp"].listdir_attr(creds["remote_path"]):
            if f_attr.filename.endswith('.md'):
                creds["sftp"].get(os.path.join(creds["remote_path"], f_attr.filename), os.path.join(mirror, f_attr.filename))

def subir_cambios_a_remoto(ruta_local, file_name, creds):
    """Empuja/Push de los archivos modificados con tags y enlaces de regreso al repositorio nube."""
    if creds["tipo"] == "gdrive":
        results = creds["service"].files().list(
            q=f"'{creds['folder_id']}' in parents and name='{file_name}' and trashed=false"
        ).execute()
        files = results.get('files', [])
        media = MediaFileUpload(ruta_local, mimeType='text/markdown')
        if files: 
            creds["service"].files().update(fileId=files[0]['id'], media_body=media).execute()
        else: 
            creds["service"].files().create(body={'name': file_name, 'parents': [creds['folder_id']]}, media_body=media).execute()
    elif creds["tipo"] == "sftp":
        creds["sftp"].put(ruta_local, os.path.join(creds["remote_path"], file_name))

# --- MÓDULO DE INTERCONEXIÓN AUTOMÁTICA (WIKILINKER CON ANTI-BROKEN LINKS) ---
def obtener_diccionario_notas(vault_path):
    """Mapea los títulos de tus notas existentes en el disco para la interconexión."""
    diccionario_titulos = {}
    for raiz, dirs, archivos in os.walk(vault_path):
        dirs[:] = [d for d in dirs if d not in IGNORAR_CARPETAS]
        for arc in archivos:
            if arc.endswith('.md') and arc != MOC_NAME and arc != CONFIG_NOTA_NAME and arc != "Historial-de-Boveda.md":
                nombre_nota = arc.replace('.md', '')
                if len(nombre_nota) >= 3:
                    diccionario_titulos[nombre_nota.lower()] = nombre_nota
    return diccionario_titulos

def aplicar_interconexion_cruzada(texto, diccionario_titulos, nota_actual):
    """Busca conceptos en el texto y genera los enlaces [[WikiLinks]] de Obsidian sin romper bloques."""
    pattern_bloques = r'(```.*?```|\[\[.*?\]\]|\[.*?\]\(.*?\))'
    partes = re.split(pattern_bloques, texto, flags=re.DOTALL)
    
    for i in range(len(partes)):
        if partes[i] and not re.match(pattern_bloques, partes[i], flags=re.DOTALL):
            for titulo_lower, titulo_real in diccionario_titulos.items():
                if titulo_real.lower() == nota_actual.lower(): continue
                # VALIDADOR INTEGRADO: re.escape + límite \b previene broken links y roturas semánticas
                patron = r'\b(' + re.escape(titulo_real) + r')\b'
                partes[i] = re.sub(patron, r'[[\1]]', partes[i], flags=re.IGNORECASE)
    return "".join(partes)

# --- MÓDULO CORE: PROCESAMIENTO ATÓMICO ---
def clasificar_y_enlazar_nota(ruta, vault_path, diccionario_titulos, criterios, modo_origen="Local"):
    if os.path.islink(ruta): return False
    try:
        if os.path.getsize(ruta) > MAX_FILE_SIZE: return False
    except: return False

    try:
        with open(ruta, 'r', encoding='utf-8', errors='ignore') as f: texto = f.read()
        nombre_actual = os.path.basename(ruta).replace('.md', '')
        
        c_analizar = texto
        match_yaml = re.match(r'^---\s*\n(.*?)\n---\s*\n', texto, re.DOTALL)
        if match_yaml: c_analizar = texto[match_yaml.end():]

        # 1. Ejecutar enlazado de conceptos cruzados
        contenido_enlazado = aplicar_interconexion_cruzada(c_analizar, diccionario_titulos, nombre_actual)

        # 2. Ejecutar análisis semántico para inyección de tags
        tags_nuevos = [tag for tag, kws in criterios.items() if any(kw in contenido_enlazado.lower() for kw in kws)]
        t_finales = sorted(tags_nuevos if tags_nuevos else ["general"])
        
        yaml_limpio = []
        if match_yaml:
            en_lista = False
            for linea in match_yaml.group(1).split('\n'):
                if linea.startswith('tags:'): en_lista = True; continue
                if en_lista and linea.startswith('  - '): continue
                else: en_lista = False
                if linea.strip(): yaml_limpio.append(linea)
            
            nuevo_yaml = "---\n" + ("\n".join(yaml_limpio) + "\n" if yaml_limpio else "") + "tags:\n" + "\n".join([f"  - {t}" for t in t_finales]) + "\n---\n"
            nuevo_contenido = nuevo_yaml + contenido_enlazado
        else:
            nuevo_contenido = "---\ntags:\n" + "\n".join([f"  - {t}" for t in t_finales]) + "\n---\n" + contenido_enlazado

        # VALIDACIÓN DE SEGURIDAD CLOUD: No re-escribir si no hay cambios reales (evita bucles mtime)
        if texto == nuevo_contenido: return False

        # 3. Escritura atómica mediante archivo temporal aislado
        dir_padre = os.path.dirname(ruta)
        with tempfile.NamedTemporaryFile('w', dir=dir_padre, delete=False, encoding='utf-8') as tf:
            tf.write(nuevo_contenido)
            temp_name = tf.name
            
        os.replace(temp_name, ruta)
        print(f"[+] Custodiada [{modo_origen}]: {os.path.basename(ruta)} -> {t_finales}")
        registrar_log(ruta, t_finales, vault_path, origen=modo_origen)
        return True
    except Exception as e:
        if 'temp_name' in locals() and os.path.exists(temp_name): os.unlink(temp_name)
        return False
def escanear_total(path, creds=None):
    modo_nombre = creds["tipo"].upper() if creds else "LOCAL"
    if creds: sincronizar_remoto_a_local(creds)
    criterios = cargar_criterios_desde_obsidian(path)
    diccionario_titulos = obtener_diccionario_notas(path)
    
    for raiz, dirs, archivos in os.walk(path):
        dirs[:] = [d for d in dirs if d not in IGNORAR_CARPETAS]
        for arc in archivos:
            if arc.endswith('.md') and arc not in {MOC_NAME, CONFIG_NOTA_NAME, "Historial-de-Boveda.md"}:
                ruta_c = os.path.join(raiz, arc)
                if clasificar_y_enlazar_nota(ruta_c, path, diccionario_titulos, criterios, modo_origen=modo_nombre):
                    if creds: subir_cambios_a_remoto(ruta_c, arc, creds)

# --- MANEJADOR DE EVENTOS PASIVOS WATCHDOG (CERO CPU) ---
if HAS_WATCHDOG:
    class ObsidianVaultHandler(FileSystemEventHandler):
        def __init__(self, vault_path, remote_creds):
            self.vault_path = vault_path
            self.remote_creds = remote_creds
            self.modo_tag = remote_creds["tipo"].upper() if remote_creds else "LOCAL"
            
        def on_modified(self, event):
            if not event.is_directory and event.src_path.endswith('.md'):
                nombre_f = os.path.basename(event.src_path)
                if nombre_f in {MOC_NAME, CONFIG_NOTA_NAME, "Historial-de-Boveda.md"}: return
                
                # Respiro milimétrico para que Obsidian termine de cerrar el descriptor del archivo
                time.sleep(0.3) 
                criterios = cargar_criterios_desde_obsidian(self.vault_path)
                diccionario_titulos = obtener_diccionario_notas(self.vault_path)
                
                if clasificar_y_enlazar_nota(event.src_path, self.vault_path, diccionario_titulos, criterios, modo_origen=self.modo_tag):
                    if self.remote_creds:
                        subir_cambios_a_remoto(event.src_path, nombre_f, self.remote_creds)

# --- BUCLE DE CAÍDA (POLLING OPTIMIZADO EN CASO DE NO TENER LIBRERÍA WATCHDOG) ---
def guardian_polling_loop(path, remote_creds=None):
    modo_tag = remote_creds["tipo"].upper() if remote_creds else "LOCAL"
    print(f"[!] WATCHDOG NO DETECTADO: Usando Polling de contingencia Cloud-Safe (Modo Pasivo 4s)...")
    tiempos = {}
    while True:
        try:
            time.sleep(4)
            if remote_creds: sincronizar_remoto_a_local(remote_creds)
            criterios = cargar_criterios_desde_obsidian(path)
            diccionario_titulos = obtener_diccionario_notas(path)
            for raiz, dirs, archivos in os.walk(path):
                dirs[:] = [d for d in dirs if d not in IGNORAR_CARPETAS]
                for arc in archivos:
                    if arc.endswith('.md') and arc not in {MOC_NAME, CONFIG_NOTA_NAME, "Historial-de-Boveda.md"}:
                        ruta = os.path.join(raiz, arc)
                        try:
                            mtime = os.path.getmtime(ruta)
                            if ruta not in tiempos or mtime > tiempos[ruta]:
                                if clasificar_y_enlazar_nota(ruta, path, diccionario_titulos, criterios, modo_origen=modo_tag):
                                    if remote_creds: subir_cambios_a_remoto(ruta, arc, remote_creds)
                                tiempos[ruta] = os.path.getmtime(ruta)
                        except: pass
        except KeyboardInterrupt: break

if __name__ == "__main__":
    config = cargar_config_json()
    credenciales_remote = None

    if config:
        print("[+] Configuración json cargada. Ejecutando en Modo Invisible/Servicio.")
        path = os.path.normpath(config.get("vault_path", ""))
        op = config.get("modo", "2")
    else:
        print("====================================================")
        print("      GUARDIÁN DE BÓVEDAS AUTOMATIZADO CLOUD PRO    ")
        print("====================================================")
        print("Entorno:\n1) Almacenamiento LOCAL\n2) Almacenamiento CLOUD (GDrive / SFTP)")
        entorno = input("Selecciona [1-2]: ").strip()
        
        if entorno == "1": path = descubrir_bovedas_locales()
        elif entorno == "2":
            credenciales_remote = inicializar_entorno_remoto()
            path = credenciales_remote["local_mirror"] if credenciales_remote else descubrir_bovedas_locales()
        else: path = descubrir_bovedas_locales()
        
        print(f"\n[+] Bóveda acoplada: {path}")
        print("\nModo:\n1) Escaneo inmediato\n2) Activar Guardián permanente")
        op = input("Selecciona [1-2]: ").strip()

    escanear_total(path, credenciales_remote)
    
    if op == "2":
        if HAS_WATCHDOG:
            print(f"\n[!] INICIANDO MOTOR WATCHDOG (Cero Consumo CPU) - Protegiendo Bóveda en tiempo real...")
            print("[*] Presione Ctrl+C para apagar la monitorización nativa.\n")
            event_handler = ObsidianVaultHandler(path, credenciales_remote)
            observer = Observer()
            observer.schedule(event_handler, path, recursive=True)
            observer.start()
            try:
                while True: time.sleep(1)
            except KeyboardInterrupt: observer.stop()
            observer.join()
        else:
            guardian_polling_loop(path, credenciales_remote)
