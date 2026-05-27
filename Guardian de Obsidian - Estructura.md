---
tags:
  - creatividad
  - humano
  - programacion
  - seguridad
---
📦 PARTE 1: Inicialización, Constantes y Sistema de Auditoría Dual (JSON + Markdown)

Copia este primer bloque y guárdalo en la parte superior de tu archivo `guardian_vault_ultimate_pro.py`. Contiene la configuración de seguridad, los diccionarios de clasificación y el motor de generación de logs duales.

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
    from [[google]].auth.transport.requests import Request
    from [[google]].oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    SCOPES = ['https://googleapis.com']
except ImportError:
    build = None

# --- CONFIGURACIÓN DE SEGURIDAD E INFRAESTRUCTURA ---
LOG_AUDITORIA = "registro_clasificaciones.json"
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB máximo por archivo
MOC_NAME = "00-Indice-General.md"

IGNORAR_CARPETAS = {
    '.obsidian', '.trash', '.git', 'attachments', 'node_modules', 'Historial',
    'Program Files', 'Program Files (x86)', 'Windows', 'AppData', 
    'System Volume Information', 'Recovery', '$Recycle.Bin', 'usr', 
    'bin', 'lib', 'var', 'etc', 'proc', 'sys', 'dev', 'boot', 'home'
}

CRITERIOS = {
    "programacion": ["python", "bash", "script", "iptables", "kernel", "router", "servidor", "network", "code", "frontend", "backend", "api"],
    "creatividad": ["diseño", "ui", "ux", "colores", "paleta", "figma", "svg", "interfaz", "brief", "layout", "tipografía", "identidad"],
    "humano": ["psicología", "filosofía", "pensamiento", "mente", "comportamiento", "emoción", "historia", "cultura", "sociedad", "cognitivo"],
    "seguridad": ["[[vpn]]", "forense", "proxy", "tunnel", "killswitch", "ofuscación", "ram", "credentials", "macchanger", "root", "nuclear", "purge"]
}

# --- MÓDULO DE AUDITORÍA DUAL (JSON + NOTA DE OBSIDIAN) ---
def registrar_log(ruta_nota, tags, vault_path, origen="Local"):
    """Registra el historial en un JSON local y actualiza de forma nativa la nota de Obsidian."""
    fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_archivo = os.path.basename(ruta_nota)
    
    # 1. Registro Estructurado en JSON
    registro = {
        "fecha_actualizacion": fecha_str, 
        "archivo": nombre_archivo, 
        "ruta_origen": os.path.normpath(ruta_nota),
        "entorno_ejecucion": origen,
        "tags_detectados": tags
    }
    datos = []
    if os.path.exists(LOG_AUDITORIA):
        try:
            with open(LOG_AUDITORIA, 'r', encoding='utf-8') as f: 
                datos = json.load(f)
        except: pass
    datos.append(registro)
    try:
        with open(LOG_AUDITORIA, 'w', encoding='utf-8') as f: 
            json.dump(datos, f, indent=4, ensure_ascii=False)
    except: pass

    # 2. Inyección Dinámica en la nota Historial-de-Boveda.md dentro de Obsidian
    if vault_path and os.path.isdir(vault_path):
        carpeta_historial = Path(vault_path) / "Historial"
        carpeta_historial.mkdir(exist_ok=True)
        nota_historial = carpeta_historial / "Historial-de-Boveda.md"
        
        # Si la nota no existe, la inicializa con la leyenda personalizada solicitada
        if not nota_historial.exists():
            with open(nota_historial, 'w', encoding='utf-8') as f:
                f.write("# 📜 Historial de Modificaciones de la Bóveda\n\n")
                f.write("> Bienvenido a tu historial de la boveda. Guardia operativo y controlando todo.\n\n")
                f.write("| Fecha y Hora | Archivo | Entorno | Tags Asignados |\n")
                f.write("| --- | --- | --- | --- |\n")
        
        # Añade la nueva fila de la nota modificada al final de la tabla de Obsidian
        with open(nota_historial, 'a', encoding='utf-8') as f:
            tags_str = ", ".join(tags)
            f.write(f"| {fecha_str} | `[[{nombre_archivo.replace('.md', '')}]]` | **{origen}** | `{tags_str}` |\n")

---------------------------------QUITAR ESTO--------------------------------------------
PARTE 2: Descubrimiento de Discos de Bajo Consumo y Conectividad Cloud Inteligente ([[Google]] Drive & SSH Key Auto-Auth)

Copia este bloque a continuación de la Parte 1. Este módulo contiene:

1. El motor que **analiza los discos de tu PC** y detecta automáticamente la ubicación de tus bóvedas para que elijas cuál custodiar.
2. El sistema de conexión a **[[Google]] Drive** con auto-creación de carpetas si no existen.
3. El módulo **SSH/SFTP** optimizado que busca de forma automática tu clave privada RSA para conectarse a servidores Linux remotamente sin pedir contraseñas.
4. ---------------------------------QUITAR ESTO--------------------------------------------
5. # --- MÓDULO DE RECONOCIMIENTO Y AUTO-DESCUBRIMIENTO DE BÓVEDAS ---
def descubrir_bovedas_locales():
    print("[*] Iniciando motor de auto-descubrimiento en el almacenamiento local...")
    print("[*] Mapeando discos físicos del sistema operativo... Por favor, espera.")
    
    raiz_disco = Path(os.path.abspath(os.sep))
    bovedas_encontradas = []

    try:
        for raiz, dirs, _ in os.walk(raiz_disco):
            # Filtrado rápido de ramas del sistema para optimizar rendimiento de I/O
            dirs[:] = [d for d in dirs if d not in IGNORAR_CARPETAS and not d.startswith('.')]
            if '.obsidian' in dirs:
                bovedas_encontradas.append(Path(raiz))
                dirs.clear() 
    except Exception as e:
        print(f"[!] Aviso durante el escaneo de disco: {e}")

    if not bovedas_encontradas:
        print("[-] No se detectó ninguna estructura de Obsidian de forma automática.")
        ruta_manual = input("[?] Por favor, ingresa manualmente la ruta absoluta de tu bóveda: ").strip()
        return os.path.normpath(ruta_manual.replace('"', '').replace("'", ""))

    print(f"\n[+] Análisis completado. Se encontraron {len(bovedas_encontradas)} bóvedas potenciales:")
    print("=" * 60)
    for idx, boveda in enumerate(bovedas_encontradas, 1):
        print(f"{idx}) {boveda}")
    print(f"{len(bovedas_encontradas) + 1}) Ingresar una ruta manualmente...")
    print("=" * 60)

    while True:
        try:
            opcion = int(input(f"Selecciona la carpeta que custodiaré [1-{len(bovedas_encontradas)+1}]: ").strip())
            if 1 <= opcion <= len(bovedas_encontradas):
                return str(bovedas_encontradas[opcion - 1])
            elif opcion == len(bovedas_encontradas) + 1:
                ruta_manual = input("[?] Ingresa manualmente la ruta absoluta de tu bóveda: ").strip()
                return os.path.normpath(ruta_manual.replace('"', '').replace("'", ""))
        except ValueError:
            print("[-] Selección inválida. Elige un número de la lista.")

# --- MÓDULO DE INFRAESTRUCTURA REMOTA ([[GOOGLE]] DRIVE & SSH/SFTP) ---
def inicializar_entorno_remoto():
    print("\n[☁️] ENTORNO REMOTO DE REPOSITORIO DE NOTAS")
    print("1) Conexión vía API oficial de [[Google]] Drive (Cloud)")
    print("2) Conexión vía Canal Seguro SSH / SFTP Directo (Servidor)")
    tipo_nube = input("Selecciona la infraestructura remota [1-2]: ").strip()
    
    temp_remote_mirror = Path(tempfile.gettempdir()) / "obsidian_remote_mirror"
    temp_remote_mirror.mkdir(exist_ok=True)

    # INFRAESTRUCTURA DE CONEXIÓN 1: [[GOOGLE]] DRIVE (CON AUTO-CREACIÓN)
    if tipo_nube == "1":
        if build is None:
            print("[-] Error: Instala las librerías de [[Google]] (`pip install [[google]]-api-python-client`).")
            return None
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    print("[-] Error: Falta archivo 'credentials.json' de [[Google]] Cloud Console.")
                    return None
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        service = build('drive', 'v3', credentials=creds)
        print("[+] Handshake con [[Google]] Drive API Exitoso.")
        folder_id = input("[?] Pega el ID de tu carpeta en Drive (o presiona Enter para crear una nueva llamada 'Obsidian_Vault_Cloud'): ").strip()
        
        # Mejora: Si se deja en blanco o no existe, crea la carpeta automáticamente en Drive
        if not folder_id:
            print("[*] Creando directorio raíz de custodia en [[Google]] Drive...")
            file_metadata = {'name': 'Obsidian_Vault_Cloud', 'mimeType': 'application/vnd.[[google]]-apps.folder'}
            folder = service.files().create(body=file_metadata, fields='id').execute()
            folder_id = folder.get('id')
            print(f"[+] Carpeta creada con éxito en la nube. ID Asignado: {folder_id}")

        return {"tipo": "gdrive", "service": service, "folder_id": folder_id, "local_mirror": str(temp_remote_mirror)}

    # INFRAESTRUCTURA DE CONEXIÓN 2: SSH / SFTP (CON LLAVE LLAVE PRIVADA AUTOMÁTICA)
    elif tipo_nube == "2":
        if paramiko is None:
            print("[-] Error: Instala Paramiko (`pip install paramiko`).")
            return None
        host = input("Servidor IP / Host SSH: ").strip()
        port = int(input("Puerto SSH (Defecto 22): ") or 22)
        user = input("Usuario SSH: ").strip()
        passwd = input("Contraseña SSH (Dejar vacío para usar llave ~/.ssh/id_rsa automáticamente): ").strip()
        remote_path = input("Ruta absoluta de la bóveda en el servidor remoto Linux: ").strip()

        try:
            transport = paramiko.Transport((host, port))
            if passwd:
                transport.connect(username=user, password=passwd)
            else:
                # Mejora: Auto-búsqueda inteligente de llaves id_rsa según el OS
                rutas_key_posibles = [
                    Path.home() / ".ssh" / "id_rsa",
                    Path("C:/Users") / user / ".ssh" / "id_rsa"
                ]
                pkey = None
                for ruta_k in rutas_key_posibles:
                    if ruta_k.exists():
                        try:
                            pkey = paramiko.RSAKey.from_private_key_file(str(ruta_k))
                            print(f"[+] Llave privada SSH detectada y cargada desde: {ruta_k}")
                            break
                        except: pass
                if not pkey:
                    raise Exception("No se encontró una llave privada id_rsa válida ni se ingresó contraseña.")
                transport.connect(username=user, pkey=pkey)
                
            sftp = paramiko.SFTPClient.from_transport(transport)
            print(f"[+] Conexión SSH/SFTP cifrada y establecida con éxito con {host}")
            return {"tipo": "sftp", "sftp": sftp, "remote_path": remote_path, "local_mirror": str(temp_remote_mirror)}
        except Exception as e:
            print(f"[-] Error crítico de infraestructura SSH: {e}")
            return None
    return None

def sincronizar_remoto_a_local(creds):
    """Descarga/Pull adaptativo de archivos remotos hacia el espejo local temporal."""
    mirror = creds["local_mirror"]
    if creds["tipo"] == "gdrive":
        results = creds["service"].files().list(
            q=f"'{creds['folder_id']}' in parents and mimeType='text/markdown' and trashed=false",
            fields="files(id, name)").execute()
        for file in results.get('files', []):
            request = creds["service"].files().get_media(fileId=file['id'])
            path_local = os.path.join(mirror, file['name'])
            with open(path_local, 'wb') as f:
                f.write(request.execute())
    elif creds["tipo"] == "sftp":
        sftp = creds["sftp"]
        try:
            for file_attr in sftp.listdir_attr(creds["remote_path"]):
                if file_attr.filename.endswith('.md'):
                    r_path = os.path.join(creds["remote_path"], file_attr.filename)
                    l_path = os.path.join(mirror, file_attr.filename)
                    sftp.get(r_path, l_path)
        except Exception as e:
            print(f"[-] Error al descargar del servidor SFTP: {e}")

def subir_cambios_a_remoto(ruta_local, file_name, creds):
    """Empuja/Push de los archivos modificados con tags y enlaces de regreso al repositorio nube."""
    if creds["tipo"] == "gdrive":
        results = creds["service"].files().list(
            q=f"'{creds['folder_id']}' in parents and name='{file_name}' and trashed=false",
            fields="files(id)").execute()
        files = results.get('files', [])
        media = MediaFileUpload(ruta_local, mimeType='text/markdown', resumable=True)
        if files:
            creds["service"].files().update(fileId=files[0]['id'], media_body=media).execute()
        else:
            file_metadata = {'name': file_name, 'parents': [creds['folder_id']]}
            creds["service"].files().create(body=file_metadata, media_body=media, fields='id').execute()
    elif creds["tipo"] == "sftp":
        r_path = os.path.join(creds["remote_path"], file_name)
        try:
            creds["sftp"].put(ruta_local, r_path)
        except Exception as e:
            print(f"[-] Error al subir cambios al servidor SFTP: {e}")
---------------------------------QUITAR ESTO--------------------------------------------
📦 PARTE 3: Motor Semántico WikiLinker, Escritura Atómica Contra Corrupción y Bucle del Guardián (Final)

Copia este último bloque a continuación de la Parte 2 para dar por finalizada la estructura de tu script. Este módulo procesa el texto plano de tus notas, inyecta los metadatos YAML, ejecuta el reemplazo seguro de palabras clave y controla los tiempos de indexación de forma pasiva.

---------------------------------QUITAR ESTO--------------------------------------------
# --- MÓDULO DE INTERCONEXIÓN AUTOMÁTICA DE CONCEPTOS (WIKILINKER) ---
def obtener_diccionario_notas(vault_path):
    """Mapea los títulos de tus notas existentes en el disco para la interconexión."""
    diccionario_titulos = {}
    for raiz, dirs, archivos in os.walk(vault_path):
        dirs[:] = [d for d in dirs if d not in IGNORAR_CARPETAS]
        for arc in archivos:
            if arc.endswith('.md') and arc != MOC_NAME:
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
                # CORRECCIÓN DE SEGURIDAD: re.escape anula caracteres regex destructivos en nombres de notas
                patron = r'\b(' + re.escape(titulo_real) + r')\b'
                partes[i] = re.sub(patron, r'[[\1]]', partes[i], flags=re.IGNORECASE)
    return "".join(partes)

# --- MÓDULO CORE: PROCESAMIENTO ATÓMICO ---
def clasificar_y_enlazar_nota(ruta, vault_path, diccionario_titulos, modo_origen="Local"):
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
        tags_nuevos = [tag for tag, kws in CRITERIOS.items() if any(kw in contenido_enlazado.lower() for kw in kws)]
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
        if texto == nuevo_contenido:
            return False

        # 3. Escritura atómica mediante archivo temporal aislado
        dir_padre = os.path.dirname(ruta)
        with tempfile.NamedTemporaryFile('w', dir=dir_padre, delete=False, encoding='utf-8') as tf:
            tf.write(nuevo_contenido)
            temp_name = tf.name
            
        os.replace(temp_name, ruta)
        print(f"[+] Custodiada [{modo_origen}]: {os.path.basename(ruta)} -> {t_finales}")
        
        # Guardar en el log JSON local y en la nota Markdown de Obsidian
        registrar_log(ruta, t_finales, vault_path, origen=modo_origen)
        return True
    except Exception as e:
        if 'temp_name' in locals() and os.path.exists(temp_name): os.unlink(temp_name)
        print(f"[-] Error en procesamiento: {e}")
        return False

def escanear_total(path, creds=None):
    modo_nombre = creds["tipo"].upper() if creds else "LOCAL"
    print(f"[*] Ejecutando indexación estructural en modo {modo_nombre}...")
    if creds:
        sincronizar_remoto_a_local(creds)

    diccionario_titulos = obtener_diccionario_notas(path)
    contador = 0
    for raiz, dirs, archivos in os.walk(path):
        dirs[:] = [d for d in dirs if d not in IGNORAR_CARPETAS]
        for arc in archivos:
            if arc.endswith('.md') and arc != MOC_NAME and arc != "Historial-de-Boveda.md":
                ruta_completa = os.path.join(raiz, arc)
                if clasificar_y_enlazar_nota(ruta_completa, path, diccionario_titulos, modo_origen=modo_nombre):
                    contador += 1
                    if creds:
                        subir_cambios_a_remoto(ruta_completa, arc, creds)
    print(f"[==>] Sincronización terminada. {contador} notas actualizadas e indexadas.")

def guardian_loop(path, remote_creds=None):
    modo_tag = remote_creds["tipo"].upper() if remote_creds else "LOCAL"
    print(f"\n[!] GUARDIÁN PROTEGIDO ACTIVO ({modo_tag}) - Ctrl+C para finalizar...\n")
    tiempos = {}
    
    while True:
        try:
            time.sleep(4)  # Intervalo pasivo de respiro de I/O para no saturar APIs ni CPU
            if remote_creds:
                sincronizar_remoto_a_local(remote_creds)

            diccionario_titulos = obtener_diccionario_notas(path)
            for raiz, dirs, archivos in os.walk(path):
                dirs[:] = [d for d in dirs if d not in IGNORAR_CARPETAS]
                for arc in archivos:
                    if arc.endswith('.md') and arc != MOC_NAME and arc != "Historial-de-Boveda.md":
                        ruta = os.path.join(raiz, arc)
                        try:
                            mtime = os.path.getmtime(ruta)
                            if ruta not in tiempos or mtime > tiempos[ruta]:
                                if clasificar_y_enlazar_nota(ruta, path, diccionario_titulos, modo_origen=modo_tag):
                                    if remote_creds: 
                                        subir_cambios_a_remoto(ruta, arc, remote_creds)
                                tiempos[ruta] = os.path.getmtime(ruta)
                        except: pass
        except KeyboardInterrupt:
            print("\n[-] Saliendo del Modo Guardián Pro de forma limpia.")
            break

# --- FLUJO PRINCIPAL DE OPERACIÓN ---
if __name__ == "__main__":
    print("====================================================")
    print("      GUARDIÁN DE BÓVEDAS AUTOMATIZADO CLOUD PRO    ")
    print("====================================================")
    print("Entorno de la Bóveda de Obsidian:")
    print("1) Almacenamiento LOCAL (Disco duro / SSD / Pendrive)")
    print("2) Almacenamiento REMOTO ([[Google]] Drive o Servidor SSH/SFTP)")
    entorno = input("Selecciona entorno [1-2]: ").strip()

    credenciales_remote = None
    if entorno == "1":
        path = descubrir_bovedas_locales()
    elif entorno == "2":
        credenciales_remote = inicializar_entorno_remoto()
        path = credenciales_remote["local_mirror"] if credenciales_remote else descubrir_bovedas_locales()
    else:
        path = descubrir_bovedas_locales()

    print(f"\n[+] Bóveda bajo custodia activa: {path}")
    print("\nModo:\n1) Escaneo único inmediato\n2) Activar Guardián permanente (Escucha Activa)")
    op = input("Selecciona [1-2]: ").strip()

    escanear_total(path, credenciales_remote)
    if op == "2":
        guardian_loop(path, credenciales_remote)
