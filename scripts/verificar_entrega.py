"""Comprobaciones estáticas de la entrega IEI_N4_C3 (sin conectar a MySQL)."""
from pathlib import Path
import sys
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
required = ['manage.py', 'crear_base_datos.sql', '.env', '.env.example', '.gitignore',
            'drf/settings.py', 'drf/urls.py', 'requirements.txt', 'README.md']
errors = []
for name in required:
    if not (ROOT / name).is_file():
        errors.append(f'Falta {name}')

# Git interpreta patrones, excepciones y directorios con sus reglas reales.
# Un repositorio temporal permite verificar también una entrega descargada como ZIP.
if shutil.which('git') is None:
    errors.append('Se necesita Git instalado para verificar las exclusiones')
elif (ROOT / '.gitignore').is_file():
    with tempfile.TemporaryDirectory() as directory:
        subprocess.run(['git', 'init', '-q', directory], check=True)
        shutil.copyfile(ROOT / '.gitignore', Path(directory) / '.gitignore')
        for name, expected in [('.env.local', True), ('mi_entorno/archivo', True),
                               ('venv/archivo', True), ('crear_base_datos_local.sql', True),
                               ('.env', False), ('.env.example', False)]:
            result = subprocess.run(
                ['git', '-c', 'core.excludesFile=', 'check-ignore', '--no-index', '-q', name],
                cwd=directory, check=False)
            if result.returncode not in (0, 1):
                errors.append(f'No se pudo comprobar la exclusión de {name}')
            elif (result.returncode == 0) != expected:
                errors.append(f'Regla incorrecta para {name}: exclusión esperada={expected}')

sql_file = ROOT / 'crear_base_datos.sql'
sql = sql_file.read_text(encoding='utf-8') if sql_file.is_file() else ''
for clause in ['CREATE DATABASE', 'CREATE USER', 'GRANT']:
    if clause not in sql:
        errors.append(f'Falta cláusula {clause} en SQL')

env_file = ROOT / '.env'
public_env = env_file.read_text(encoding='utf-8') if env_file.is_file() else ''
for key in ['DJANGO_SECRET_KEY=', 'DB_NAME=', 'DB_USER=', 'DB_PASSWORD=']:
    if key not in public_env:
        errors.append(f'Falta {key} en .env')

if (ROOT / '.env.local').exists():
    errors.append('Un .env.local privado está presente en el paquete: no publicarlo')

if errors:
    print('FALLO EN VERIFICACION ESTATICA:')
    for error in errors:
        print(' -', error)
    sys.exit(1)
print('OK: requisitos de archivos y SQL detectados. No verifica conexion real a MySQL.')
