@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist manage.py if exist ..\manage.py cd ..
echo === Actualizar y abrir Voluntariados ===
echo Este archivo debe estar junto a manage.py, en la carpeta del proyecto.
echo.
if not exist manage.py (
  echo No encuentro manage.py. Mueve este archivo a la carpeta del proyecto.
  goto :error
)
where git >nul 2>nul
if errorlevel 1 (
  echo No encuentro Git. Envia una captura de esta ventana para revisar la instalacion.
  goto :error
)
git rev-parse --show-toplevel >nul 2>nul
if errorlevel 1 (
  echo Esta carpeta no es una copia Git. No se modifico ningun archivo.
  goto :error
)
rem Valida el repositorio y conserva los cambios locales antes de actualizar.
powershell -NoProfile -Command "$root=(git rev-parse --show-toplevel); if ((Resolve-Path .).Path -ne (Resolve-Path $root).Path) { Write-Host 'El lanzador debe estar en la raiz del repositorio.'; exit 1 }; $remote=git remote get-url origin; if ($remote -notmatch '^https://github\.com/anaantihu-ui/IEI_N4_C3(?:\.git)?/?$|^git@github\.com:anaantihu-ui/IEI_N4_C3(?:\.git)?$') { Write-Host 'La carpeta pertenece a otro repositorio. No se modifico.'; exit 1 }; $changes=@(git status --porcelain --untracked-files=all | Where-Object { $_ -ne '?? actualizar_y_abrir.cmd' }); if ($changes.Count -gt 0) { Write-Host 'Hay cambios locales. Me detengo para conservarlos:'; $changes | ForEach-Object { Write-Host $_ }; exit 1 }"
if errorlevel 1 goto :error
rem No permitir que el cambio de rama sobrescriba un .env privado ignorado.
if exist .env (
  git ls-files --error-unmatch .env >nul 2>nul
  if errorlevel 1 (
    echo Se encontro un .env privado no versionado. Me detengo para conservarlo.
    echo Envia una captura de este aviso, sin mostrar el contenido de .env.
    goto :error
  )
)
git fetch origin implementacion/voluntariados
if errorlevel 1 goto :error
git switch implementacion/voluntariados
if errorlevel 1 goto :error
git merge --ff-only origin/implementacion/voluntariados
if errorlevel 1 goto :error
if not exist .venv\Scripts\python.exe (
  py -3.12 -m venv .venv
  if errorlevel 1 py -3.11 -m venv .venv
  if errorlevel 1 goto :error
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :error
.venv\Scripts\python.exe scripts\abrir_web_local.py
if errorlevel 1 goto :error
exit /b 0
:error
echo.
echo No se completo el inicio. Envia una captura de esta ventana, sin contrasenas.
echo No se borraron cambios locales ni se detuvo ningun otro servidor.
pause
exit /b 1
