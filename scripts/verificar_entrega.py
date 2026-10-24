"""Comprobaciones estáticas de la entrega IEI_N4_C3 (sin conectar a MySQL)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
required = ['manage.py', 'crear_base_datos.sql', '.env', '.env.example', '.gitignore',
            'drf/settings.py', 'drf/urls.py', 'requirements.txt', 'README.md']
errors = []
for name in required:
    if not (ROOT / name).is_file():
        errors.append(f'Falta {name}')

ignore = (ROOT / '.gitignore').read_text(encoding='utf-8')
for name in ['.env.local', 'mi_entorno/', 'venv/']:
    if name not in ignore:
        errors.append(f'.gitignore no excluye {name}')

sql = (ROOT / 'crear_base_datos.sql').read_text(encoding='utf-8')
for clause in ['CREATE DATABASE', 'CREATE USER', 'GRANT']:
    if clause not in sql:
        errors.append(f'Falta cláusula {clause} en SQL')

public_env = (ROOT / '.env').read_text(encoding='utf-8')
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
