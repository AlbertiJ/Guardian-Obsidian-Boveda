#!/usr/bin/env python3
import os
import re
import sys
import time
import json
import tempfile
import subprocess
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

# --- CONFIGURACIÓN GLOBAL E INFRAESTRUCTURA ---
DIRECTORIO_ACTUAL = Path(__file__).parent.resolve()
SCRIPT_AUTOCONTENIDO = Path(__file__).resolve()
LOG_AUDITORIA = DIRECTORIO_ACTUAL / "registro_clasificaciones.json"
CONFIG_FILE = DIRECTORIO_ACTUAL / "config.json"

CONFIG_NOTA_NAME = "Configuracion-Guardian.md"
HISTORIAL_NOTA_NAME = Path("Historial") / "Historial-de-Boveda.md"
MOC_NAME = "00-Indice-General.md"
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB máximo por nota

IGNORAR_CARPETAS = {
    '.obsidian', '.trash', '.git', 'attachments', 'node_modules', 'Historial',
    'Program Files', 'Program Files (x86)', 'Windows', 'AppData', 
    'System Volume Information', 'Recovery', '$Recycle.Bin', 'usr', 
    'bin', 'lib', 'var', 'etc', 'proc', 'sys', 'dev', 'boot', 'home'
}

CRITERIOS_DEFAULT = {
    "programacion": ["python", "bash", "script", "iptables", "servidor", "api", "code"],
    "seguridad": ["vpn", "forense", "proxy", "killswitch", "credentials", "root"]
}

# --- CONTROLADOR DE INSTANCIAS EN MEMORIA ---
def limpiar_procesos_anteriores():
    """Busca y elimina instancias previas para evitar duplicados en la RAM de forma nativa."""
    mi_nombre = SCRIPT_AUTOCONTENIDO.name
    if sys.platform == "win32":
        cmd_kill = f"Get-CimInstance Win32_Process -Filter \"CommandLine LIKE '%{mi_nombre}%' AND ProcessId <> {os.getpid()}\" | Remove-CimInstance"
        subprocess.run(["powershell", "-Command", cmd_kill], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        # Comando nativo UNIX excluyendo nuestro propio PID actual
        cmd_pkill = f"pkill -f '{mi_nombre}'"
        subprocess.run(f"pgrep -f '{mi_nombre}' | grep -v {os.getpid()} | xargs kill -9", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# --- LECTOR DINÁMICO DE CONFIGURACIÓN MARKDOWN ---
def cargar_criterios_desde_obsidian(vault_path):
    """Parsea Configuracion-Guardian.md para extraer tags, keywords y exclusiones de forma dinámica."""
    ruta_config_nota = Path(vault_path) / CONFIG_NOTA_NAME
    criterios = {}
    notas_excluidas = set()
    
    if not ruta_config_nota.exists():
        return CRITERIOS_DEFAULT, notas_excluidas

    try:
        with open(ruta_config_nota, 'r', encoding='utf-8') as f:
            for linea in f:
                if ":" in linea and not linea.startswith("#") and not linea.startswith(">"):
                    parts = linea.split(":", 1)
                    tag = parts[0].strip().lower()
                    
                    if tag == "notas_protegidas":
                        notas_excluidas = {n.strip() for n in parts[1].split(",") if n.strip()}
                    else:
                        keywords = [k.strip().lower() for k in parts[1].split(",") if k.strip()]
                        if tag and keywords:
                            criterios[tag] = keywords
        return (criterios if criterios else CRITERIOS_DEFAULT), notas_excluidas
    except:
        return CRITERIOS_DEFAULT, notas_excluidas

# --- GESTOR DE ENTORNO PORTABLE (JSON CONFIG) ---
def gestionar_config_json():
    """Garantiza la existencia del config.json para la persistencia del demonio."""
    if not CONFIG_FILE.exists():
        # Intentar auto-detectar si hay una carpeta de Obsidian al lado del script
        boveda_sugerida = DIRECTORIO_ACTUAL / "Mobil01"
        if not boveda_sugerida.exists():
            boveda_sugerida = DIRECTORIO_ACTUAL
            
        print(f"[!] Archivo config.json no detectado.")
        ruta_boveda = input(f"[?] Introduce la ruta de tu bóveda [Por defecto: {boveda_sugerida}]: ").strip()
        if not ruta_boveda:
            ruta_boveda = str(boveda_sugerida)
        
        config_data = {
            "vault_path": os.path.normpath(ruta_boveda.replace('"', '').replace("'", "")),
            "modo": "2"
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return None
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
    if creds["tipo"] == "gdrive":
        results = creds["service"].files().list(q=f"'{creds['folder_id']}' in parents and name='{file_name}' and trashed=false").execute()
        files = results.get('files', [])
        media = MediaFileUpload(ruta_local, mimeType='text/markdown')
        if files: creds["service"].files().update(fileId=files[0]['id'], media_body=media).execute()
        else: creds["service"].files().create(body={'name': file_name, 'parents': [creds['folder_id']]}, media_body=media).execute()
    elif creds["tipo"] == "sftp":
        creds["sftp"].put(ruta_local, os.path.join(creds["remote_path"], file_name))

# --- MOTOR DE INTERCONEXIÓN (WIKILINKER ANTI-BROKEN) ---
def obtener_diccionario_notas(vault_path):
    diccionario_titulos = {}
    for raiz, dirs, archivos in os.walk(vault_path):
        dirs[:] = [d for d in dirs if d not in IGNORAR_CARPETAS]
        for arc in archivos:
            if arc.endswith('.md') and arc not in {MOC_NAME, CONFIG_NOTA_NAME, os.path.basename(HISTORIAL_NOTA_NAME)}:
                nombre_nota = arc.replace('.md', '')
                if len(nombre_nota) >= 3:
                    diccionario_titulos[nombre_nota.lower()] = nombre_nota
    return diccionario_titulos

def aplicar_interconexion_cruzada(texto, diccionario_titulos, nota_actual):
    pattern_bloques = r'(```.*?```|\[\[.*?\]\]|\[.*?\]\(.*?\))'
    partes = re.split(pattern_bloques, texto, flags=re.DOTALL)
    for i in range(len(partes)):
        if partes[i] and not re.match(pattern_bloques, partes[i], flags=re.DOTALL):
            for titulo_lower, titulo_real in diccionario_titulos.items():
                if titulo_real.lower() == nota_actual.lower(): continue
                patron = r'\b(' + re.escape(titulo_real) + r')\b'
                partes[i] = re.sub(patron, r'[[\1]]', partes[i], flags=re.IGNORECASE)
    return "".join(partes)

# --- INTERFAZ INTERACTIVA Y FILTRADO POR FECHAS ---
def actualizar_interfaz_historial(vault_path, ruta_nota, tipo_evento, tags, origen):
    # Resolver la ruta absoluta de forma inequívoca
    nota_historial = Path(vault_path) / "Historial" / "Historial-de-Boveda.md"
    if not nota_historial.exists(): return

    fecha_actual = datetime.now()
    fecha_str = fecha_actual.strftime("%Y-%m-%d %H:%M:%S")
    
    nuevo_registro = {
        "fecha": fecha_str,
        "timestamp_creacion": os.path.getctime(ruta_nota) if os.path.exists(ruta_nota) else time.time(),
        "timestamp_modificacion": os.path.getmtime(ruta_nota) if os.path.exists(ruta_nota) else time.time(),
        "evento": tipo_evento,
        "archivo": os.path.basename(ruta_nota),
        "entorno": origen,
        "tags": tags
    }
    
    logs = []
    if os.path.exists(LOG_AUDITORIA):
        try:
            with open(LOG_AUDITORIA, 'r', encoding='utf-8') as f: logs = json.load(f)
        except: pass
    logs.append(nuevo_registro)
    try:
        with open(LOG_AUDITORIA, 'w', encoding='utf-8') as f: json.dump(logs, f, indent=4, ensure_ascii=False)
    except: pass

    try:
        with open(nota_historial, 'r', encoding='utf-8') as f: contenido_h = f.read()
    except: return

    # Buscador avanzado mediante Regex para la configuración de raíz
    def buscar_valor_yaml(clave, texto_fuente, defecto=""):
        match = re.search(fr'^{clave}:\s*["\']?(.*?)["\']?\s*$', texto_fuente, re.MULTILINE | re.IGNORECASE)
        return match.group(1).strip() if match else defecto

    limite = buscar_valor_yaml("limite_resultados", contenido_h, "20")
    filtro_mes = buscar_valor_yaml("filtro_fecha", contenido_h, "")
    rango_desde = buscar_valor_yaml("rango_desde", contenido_h, "")
    rango_hasta = buscar_valor_yaml("rango_hasta", contenido_h, "")
    criterio_orden = buscar_valor_yaml("criterio_orden", contenido_h, "modificacion")
    exportar = buscar_valor_yaml("solicitar_exportacion", contenido_h, "false").lower() == "true"

    logs_filtrados = logs.copy()
    if filtro_mes: logs_filtrados = [l for l in logs_filtrados if l["fecha"].startswith(filtro_mes)]
    if rango_desde and rango_hasta: logs_filtrados = [l for l in logs_filtrados if rango_desde <= l["fecha"][:10] <= rango_hasta]
        
    if criterio_orden == "creacion": logs_filtrados.sort(key=lambda x: x["timestamp_creacion"], reverse=True)
    else: logs_filtrados.sort(key=lambda x: x["timestamp_modificacion"], reverse=True)

    if str(limite).isdigit(): logs_filtrados = logs_filtrados[:int(limite)]

    tabla_render = "| Fecha y Hora | Tipo Evento | Archivo | Entorno | Tags Asignados |\n| --- | --- | --- | --- | --- |\n"
    for l in logs_filtrados:
        tags_str = ", ".join([f"`#{t}`" for t in l["tags"]])
        tabla_render += f"| {l['fecha']} | {l['evento']} | `[[{l['archivo'].replace('.md', '')}]]` | **{l['entorno']}** | {tags_str} |\n"

    json_render = "```json\n// Cambia 'solicitar_exportacion' a true en el Frontmatter superior para exportar.\n```"
    if exportar:
        json_render = f"```json\n{json.dumps(logs_filtrados, indent=2, ensure_ascii=False)}\n```"
        contenido_h = contenido_h.replace("solicitar_exportacion: true", "solicitar_exportacion: false")

    # --- REEMPLAZO SEGURO MEDIANTE ÍNDICES FIJOS (INMUNE A COMPLEJIDAD DE TIPOS) ---
    ancla_tabla_inicio = "<!-- START_GUARDIAN_RENDER -->"
    ancla_tabla_fin = "<!-- END_GUARDIAN_RENDER -->"

    if ancla_tabla_inicio in contenido_h and ancla_tabla_fin in contenido_h:
        idx_inicio = contenido_h.find(ancla_tabla_inicio) + len(ancla_tabla_inicio)
        idx_fin = contenido_h.find(ancla_tabla_fin)

        # Extraer lo que está antes del inicio y lo que está después del fin
        antes = contenido_h[:idx_inicio]
        despues = contenido_h[idx_fin:]

        # Ensamblar el nuevo contenido de la tabla
        contenido_h = antes + "\n\n" + tabla_render + "\n" + despues

    ancla_json_inicio = "<!-- START_GUARDIAN_JSON -->"
    ancla_json_fin = "<!-- END_GUARDIAN_JSON -->"

    if ancla_json_inicio in contenido_h and ancla_json_fin in contenido_h:
        idx_j_inicio = contenido_h.find(ancla_json_inicio) + len(ancla_json_inicio)
        idx_j_fin = contenido_h.find(ancla_json_fin)

        antes_j = contenido_h[:idx_j_inicio]
        despues_j = contenido_h[idx_j_fin:]

        # Ensamblar el nuevo bloque de código JSON
        contenido_h = antes_j + "\n" + json_render + "\n" + despues_j

    # Escritura física y definitiva en el disco
    try:
        with open(nota_historial, 'w', encoding='utf-8') as f:
            f.write(contenido_h)
    except Exception as e:
        print(f"[-] Fallo crítico de escritura en disco: {e}")
# --- PROCESAMIENTO ATÓMICO NO DESTRUCTIVO ---
def clasificar_y_enlazar_nota(ruta, vault_path, diccionario_titulos, criterios, notas_excluidas, modo_origen="LOCAL", evento="Modificación"):
    if os.path.islink(ruta): return False
    nombre_actual = os.path.basename(ruta).replace('.md', '')
    if nombre_actual in notas_excluidas: return False
    try:
        if os.path.getsize(ruta) > MAX_FILE_SIZE: return False
    except: return False

    try:
        with open(ruta, 'r', encoding='utf-8', errors='ignore') as f: texto = f.read()
        
        # --- DETECCIÓN DE CAMBIO POR TIMESTAMP (Sincronización con Historial) ---
        mtime_actual = os.path.getmtime(ruta)
        cambio_detectado = False
        
        if os.path.exists(LOG_AUDITORIA):
            try:
                with open(LOG_AUDITORIA, 'r', encoding='utf-8') as f_log:
                    logs = json.load(f_log)
                    # Buscar el último registro de este archivo específico
                    ultimo_reg = next((l for l in reversed(logs) if l["archivo"] == nombre_actual + '.md'), None)
                    if ultimo_reg:
                        last_mtime = ultimo_reg.get("timestamp_modificacion", 0)
                        if mtime_actual > last_mtime:
                            cambio_detectado = True
            except: pass
        else:
            cambio_detectado = True # Forzar registro si no hay log

        c_analizar = texto
        match_yaml = re.match(r'^---\s*\n(.*?)\n---\s*\n', texto, re.DOTALL)
        tags_preexistentes = set()

        if match_yaml:
            c_analizar = texto[match_yaml.end():]
            en_lista = False
            yaml_limpio = []
            for linea in match_yaml.group(1).split('\n'):
                if linea.startswith('tags:'):
                    en_lista = True
                    inline = re.findall(r'\[(.*?)\]', linea)
                    if inline: tags_preexistentes.update([t.strip() for t in inline[0].split(',') if t.strip()])
                    continue
                if en_lista and linea.startswith('  - '):
                    tags_preexistentes.add(linea.replace('  - ', '').strip())
                    continue
                elif en_lista and not linea.startswith('  - '): en_lista = False
                if linea.strip(): yaml_limpio.append(linea)

        contenido_enlazado = aplicar_interconexion_cruzada(c_analizar, diccionario_titulos, nombre_actual)
        tags_nuevos = [tag for tag, kws in criterios.items() if any(kw in contenido_enlazado.lower() for kw in kws)]
        
        # PRESERVACIÓN STRICT: Unión de conjuntos sin alterar tags preexistentes
        t_finales = sorted(list(tags_preexistentes.union(tags_nuevos))) if (tags_nuevos or tags_preexistentes) else ["general"]
        
        if match_yaml:
            nuevo_yaml = "---\n" + ("\n".join(yaml_limpio) + "\n" if yaml_limpio else "") + "tags:\n" + "\n".join([f"  - {t}" for t in t_finales]) + "\n---\n"
            nuevo_contenido = nuevo_yaml + contenido_enlazado
        else:
            nuevo_contenido = "---\ntags:\n" + "\n".join([f"  - {t}" for t in t_finales]) + "\n---\n" + contenido_enlazado

        # SI hay un cambio en el contenido O si el timestamp indica modificación, registramos en el historial
        if texto != nuevo_contenido or cambio_detectado:
            if texto != nuevo_contenido:
                dir_padre = os.path.dirname(ruta)
                with tempfile.NamedTemporaryFile('w', dir=dir_padre, delete=False, encoding='utf-8') as tf:
                    tf.write(nuevo_contenido)
                    temp_name = tf.name
                os.replace(temp_name, ruta)
            
            actualizar_interfaz_historial(vault_path, ruta, evento, t_finales, modo_origen)
            return True
        
        return False
    except:
        if 'temp_name' in locals() and os.path.exists(temp_name): os.unlink(temp_name)
        return False

def escanear_total(path, creds=None, primer_lanzamiento=False):
    if creds: sincronizar_remoto_a_local(creds)
    criterios, notas_excluidas = cargar_criterios_desde_obsidian(path)
    diccionario_titulos = obtener_diccionario_notas(path)
    evento = "Primer Lanzamiento" if primer_lanzamiento else "Escaneo"

    # CONTADORES DE ACTIVIDAD VISIBLES DEL GUARDIÁN
    total_procesados = 0
    total_registrados = 0

    print("[*] Guardián inspeccionando el sistema de archivos...")

    for raiz, dirs, archivos in os.walk(path):
        dirs[:] = [d for d in dirs if d not in IGNORAR_CARPETAS]
        for arc in archivos:
            total_procesados += 1
            if arc.endswith('.md') and arc not in {os.path.basename(HISTORIAL_NOTA_NAME), CONFIG_NOTA_NAME, MOC_NAME}:
                ruta_c = os.path.join(raiz, arc)
                
                modo = creds["tipo"].upper() if creds else "LOCAL"
                if clasificar_y_enlazar_nota(ruta_c, path, diccionario_titulos, criterios, notas_excluidas, modo, evento):
                    total_registrados += 1
                    if creds: subir_cambios_a_remoto(ruta_c, arc, creds)

    # Despliegue de métricas vivas en tu terminal de PowerShell
    print(f"[+] Análisis completado con éxito.")
    print(f"[*] Total de archivos .md inspeccionados: {total_procesados}")
    print(f"[*] Total de archivos modificados/registrados en historial: {total_registrados}")

# --- WATCHDOG / POLLING COUPLING ---
if HAS_WATCHDOG:
    class ObsidianVaultHandler(FileSystemEventHandler):
        def __init__(self, vault_path, remote_creds):
            self.vault_path = vault_path
            self.remote_creds = remote_creds
            self.modo_tag = remote_creds["tipo"].upper() if remote_creds else "LOCAL"
            self.ultimos_procesados = {}
            
        def on_modified(self, event):
            if not event.is_directory and event.src_path.endswith('.md'):
                ruta = event.src_path
                nombre_f = os.path.basename(ruta)
                if nombre_f in {os.path.basename(HISTORIAL_NOTA_NAME), CONFIG_NOTA_NAME, MOC_NAME}: return
                try:
                    mtime = os.path.getmtime(ruta)
                    if ruta in self.ultimos_procesados and mtime <= self.ultimos_procesados[ruta]: return
                    time.sleep(1.5)
                    criterios, notas_excluidas = cargar_criterios_desde_obsidian(self.vault_path)
                    diccionario_titulos = obtener_diccionario_notas(self.vault_path)
                    if clasificar_y_enlazar_nota(ruta, self.vault_path, diccionario_titulos, criterios, notas_excluidas, self.modo_tag, "Modificación"):
                        self.ultimos_procesados[ruta] = os.getmtime(ruta)
                        if self.remote_creds: subir_cambios_a_remoto(ruta, nombre_f, self.remote_creds)
                    else: self.ultimos_procesados[ruta] = mtime
                except: pass

def guardian_polling_loop(path, remote_creds=None):
    modo_tag = remote_creds["tipo"].upper() if remote_creds else "LOCAL"
    tiempos = {}
    while True:
        try:
            time.sleep(4)
            if remote_creds: sincronizar_remoto_a_local(remote_creds)
            criterios, notas_excluidas = cargar_criterios_desde_obsidian(path)
            diccionario_titulos = obtener_diccionario_notas(path)
            for raiz, dirs, archivos in os.walk(path):
                dirs[:] = [d for d in dirs if d not in IGNORAR_CARPETAS]
                for arc in archivos:
                    if arc.endswith('.md') and arc not in {os.path.basename(HISTORIAL_NOTA_NAME), CONFIG_NOTA_NAME, MOC_NAME}:
                        ruta = os.path.join(raiz, arc)
                        try:
                            mtime = os.path.getmtime(ruta)
                            if ruta not in tiempos or mtime > tiempos[ruta]:
                                if clasificar_y_enlazar_nota(ruta, path, diccionario_titulos, criterios, notas_excluidas, modo_tag, "Modificación"):
                                    if remote_creds: subir_cambios_a_remoto(ruta, arc, remote_creds)
                                tiempos[ruta] = os.path.getmtime(ruta)
                        except: pass
        except KeyboardInterrupt: break

# --- ORQUESTADOR UNIFICADO (LANZADOR INVISIBLE INTERNO) ---
def lanzar_demonio_oculto():
    limpiar_procesos_anteriores()
    config = gestionar_config_json()
    if not config: sys.exit(1)
    
    print("[+] Desplegando Guardián en segundo plano verdadero...")
    if sys.platform == "win32":
        # Comando PowerShell nativo con ventana completamente oculta
        comando_ps = f"Start-Process '{sys.executable}' -ArgumentList '\"{SCRIPT_AUTOCONTENIDO}\" --serve' -WindowStyle Hidden"
        subprocess.Popen(["powershell", "-Command", comando_ps], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        with open(os.devnull, 'r') as devnull:
            subprocess.Popen([sys.executable, str(SCRIPT_AUTOCONTENIDO), "--serve"],
                             stdin=devnull, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
    print("[🚀] ¡Guardián operativo y controlando todo desde las sombras!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg_val = sys.argv[1].lower()
        
        if arg_val == "stop":
            limpiar_procesos_anteriores()
            print("[🛑] El Guardián ha sido desactivado y removido de la memoria.")
            sys.exit(0)
            
        elif arg_val == "--serve":
            config = gestionar_config_json()
            if not config: 
                sys.exit(1)
            
            path = os.path.normpath(config.get("vault_path", ""))
            (Path(path) / "Historial").mkdir(exist_ok=True)
            
            # Forzamos el uso del bucle de Polling Pasivo para evitar bloqueos de Windows
            guardian_polling_loop(path, None)
            sys.exit(0)

    # MENÚ CONSOLA INTERACTIVO (Si se ejecuta sin argumentos)
    print("====================================================")
    print("        SISTEMA UNIFICADO GUARDIÁN DE OBSIDIAN       ")
    print("====================================================")
    print("1) Arrancar Guardián Oculto (Primer Lanzamiento + Fondo)")
    print("2) Detener Guardián por Completo")
    print("3) Solo Escaneo Inmediato")
    op = input("Selecciona [1-3]: ").strip()
    
    if op == "1":
        config = gestionar_config_json()
        if config:
            path = os.path.normpath(config.get("vault_path", ""))
            (Path(path) / "Historial").mkdir(exist_ok=True)
            print("[*] Ejecutando escaneo de primer lanzamiento (Preservando tags)...")
            escanear_total(path, primer_lanzamiento=True)
            lanzar_demonio_oculto()
    elif op == "2":
        limpiar_procesos_anteriores()
        print("[🛑] Desactivado de la memoria.")
    elif op == "3":
        config = gestionar_config_json()
        if config:
            path = os.path.normpath(config.get("vault_path", ""))
            escanear_total(path)
            print("[+] Escaneo atómico finalizado.")
    else:
        print("[-] Opción inválida.")
