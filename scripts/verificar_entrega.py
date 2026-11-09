"""Comprueba archivos y coherencia de la configuración pública; no sustituye los tests."""
from pathlib import Path
import ast
import subprocess
import tempfile
import shutil

root = Path(__file__).resolve().parents[1]
required = ['manage.py', '.env', '.env.example', '.gitignore', 'requirements.txt', 'README.md',
            'crear_base_datos.sql', 'scripts/permisos_pruebas.sql', 'drf/settings.py', 'drf/urls.py',
            'comunidad/models.py', 'comunidad/serializers.py', 'comunidad/views.py', 'comunidad/urls.py',
            'comunidad/migrations/0001_initial.py', 'comunidad/tests.py', 'docs/MODELO_Y_REGLAS.md']
errors = [f'Falta {p}' for p in required if not (root/p).is_file()]
env_text = (root/'.env').read_text()
if env_text != (root/'.env.example').read_text():
    errors.append('.env y .env.example difieren')
values = dict(line.split('=', 1) for line in env_text.splitlines() if '=' in line and not line.startswith('#'))
sql = (root/'crear_base_datos.sql').read_text()
for key in ['DB_NAME', 'DB_USER', 'DB_PASSWORD']:
    if not values.get(key) or values[key] not in sql:
        errors.append(f'{key} no coincide con el SQL')
if not values.get('DJANGO_SECRET_KEY'):
    errors.append('Falta DJANGO_SECRET_KEY')
tree = ast.parse((root/'drf/settings.py').read_text())
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SECRET_KEY' for t in node.targets):
        if not isinstance(node.value, ast.Call):
            errors.append('SECRET_KEY debe leerse desde el entorno')
if shutil.which('git'):
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['git', 'init', '-q', d], check=True)
        shutil.copy(root/'.gitignore', Path(d)/'.gitignore')
        for name, ignored in [('.env', False), ('.env.example', False), ('.env.local', True), ('crear_base_datos_local.sql', True), ('.venv/archivo', True)]:
            result = subprocess.run(['git', '-c', 'core.excludesFile=', 'check-ignore', '--no-index', '-q', name], cwd=d)
            if result.returncode not in [0, 1] or (result.returncode == 0) != ignored:
                errors.append(f'Exclusión incorrecta: {name}')
else:
    errors.append('Se necesita Git para comprobar exclusiones')
if errors:
    raise SystemExit('\n'.join(errors))
print('OK: archivos, SQL y entorno coherentes. Ejecuta migrate y test para verificar funcionamiento.')
