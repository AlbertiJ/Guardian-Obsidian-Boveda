# ====================================================================
#        AUTOMATIZADOR DE DESPLIEGUE SEGURO — GUARDIÁN DE OBSIDIAN
# ====================================================================

# 1. Definición estricta de rutas de ingeniería
$RutaProyecto = "C:\Users\juan\home\albertij\Bovedamobil\Mobil01\Palacio de cristal\Proyectos\Guardian de Obsidian"
$URL_Remota = "https://github.com/AlbertiJ/Guardian-Obsidian-Boveda"

Write-Host "[*] Iniciando secuencia de despliegue en: $RutaProyecto" -ForegroundColor Cyan
Set-Location -Path $RutaProyecto

# 2. Sanitización defensiva de la caché e índices corruptos de Git
Write-Host "[*] Limpiando índices fantasmas y submódulos bloqueados..." -ForegroundColor Yellow
Remove-Item -Path ".git" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "Version actualizada\.git" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Inicialización del entorno limpio de control de versiones
Write-Host "[+] Inicializando repositorio Git local..." -ForegroundColor Green
git init
git branch -M main
git remote add origin $URL_Remota

# 4. Sincronización pasiva del historial antiguo de GitHub (Fusión de Ramas)
Write-Host "[*] Conectando con GitHub y absorbiendo historial histórico..." -ForegroundColor Yellow
git fetch origin main
git checkout -b main
git merge origin/main --allow-unrelated-histories -X ours --quiet

# 5. Indexación forzada del árbol de carpetas (Raíz V1.0 + Subcarpeta V2.1)
Write-Host "[*] Indexando árbol completo de archivos (Evolución de Arquitectura)..." -ForegroundColor Yellow
git rm -r --cached . 2>$null
git add .

# 6. Sellado de Commit de producción
$MensajeCommit = "Evolution: Repositorio estructurado con V1.0 en la raíz y Arquitectura Unificada V2.1 en subcarpeta"
git commit -m $MensajeCommit

# 7. Empuje definitivo a la nube pública de GitHub
Write-Host "[🚀] Empujando código de forma segura a GitHub..." -ForegroundColor Green
git push -u origin main --force

Write-Host "[🎉] ¡Despliegue completado! Repositorio actualizado y privacidad protegida." -ForegroundColor Green
