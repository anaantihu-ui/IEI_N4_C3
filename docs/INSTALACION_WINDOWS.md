# Instalación en tu computador: Windows, phpMyAdmin y MariaDB 10.4.32

Estas instrucciones se ejecutan en TU computador. localhost se refiere al equipo
que abre la dirección. Las pruebas del asistente ocurren en un entorno separado.
No se ha accedido a tu phpMyAdmin ni aplicado migraciones en tu servidor.

## 1. Obtener el código de la rama correcta

Abre PowerShell en una carpeta para proyectos. Si todavía no tienes una copia:

```powershell
git clone --branch implementacion/voluntariados https://github.com/anaantihu-ui/IEI_N4_C3.git
cd IEI_N4_C3
```

Si ya tienes una copia, abre su carpeta en la terminal y ejecuta primero
`git status`. Conserva cualquier trabajo local antes de cambiar de rama; no uses
reset --hard. Con la copia sin cambios pendientes:

```powershell
git switch implementacion/voluntariados
git pull --ff-only
git branch --show-current
```

Debe mostrar implementacion/voluntariados. La carpeta contiene manage.py.

## 2. Crear la base desde phpMyAdmin

1. Inicia Apache y MySQL en XAMPP. Aunque el botón diga MySQL, tu motor es MariaDB.
2. Abre http://localhost/phpmyadmin/ con tu cuenta administradora local.
3. Pulsa el nombre del servidor/inicio y luego **SQL**. No selecciones incidencias.
4. Abre `crear_base_datos.sql` del proyecto en un editor. Copia todo su contenido,
   pégalo en SQL y pulsa **Continuar**. Solo se crea voluntariados y sus usuarios.
5. Actualiza el árbol izquierdo: debe aparecer **voluntariados**. Al principio
   estará vacía: Django creará las tablas en el paso 4.
6. En SQL ejecuta `SELECT VERSION();` y conserva el resultado 10.4.32-MariaDB.
7. Verifica los resultados de SHOW GRANTS: los permisos de aplicación corresponden
   a voluntariados.*. USAGE ON *.* no concede acceso a las tablas de otras bases.

El SQL usa exclusivamente claves de demostración. CREATE USER IF NOT EXISTS no
cambia claves de cuentas existentes. Si ya existe voluntariados_app con otra clave,
usa esa clave en .env.local; no compartas capturas que la muestren. Si SHOW GRANTS
muestra permisos globales heredados, usa una cuenta nueva dedicada antes de seguir.

phpMyAdmin es la herramienta de administración; Django conecta directamente a
MariaDB en 127.0.0.1:3306, no a la URL /phpmyadmin/.

## 3. Preparar Python y las variables

En PowerShell, dentro de la carpeta que contiene manage.py:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m django --version
Copy-Item .env.example .env.local
```

Debe indicar Django 4.2.30. Usa Python 3.11 o 3.12, no 3.13/3.14 para esta versión.
No necesitas activar el entorno si usas la ruta completa al ejecutable.
Si ya existe .env.local, revísalo en lugar de sobrescribirlo.

Abre .env.local en un editor. Para la demo debe mantener:

```dotenv
DB_ENGINE=mysql
DB_NAME=voluntariados
DB_USER=voluntariados_app
DB_PASSWORD=demo_voluntariados2026
DB_HOST=127.0.0.1
DB_PORT=3306
DB_TEST_NAME=test_voluntariados
```

Si el puerto de XAMPP es otro, modifica DB_PORT. Para claves reales, cambia el SQL
EN UNA COPIA `crear_base_datos_local.sql` y .env.local; ambos están ignorados por Git.
Genera una SECRET_KEY privada y pega el resultado solo en DJANGO_SECRET_KEY de .env.local:

```powershell
.\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

El .env público queda intacto para el profesor. Las variables de Windows prevalecen
sobre los archivos. Si habías definido DB_ENGINE=sqlite, ejecuta
`Remove-Item Env:DB_ENGINE -ErrorAction SilentlyContinue` antes de conectar a MariaDB.

## 4. Comprobar la conexión y crear las tablas

Ejecuta en la misma terminal y carpeta:

```powershell
.\.venv\Scripts\python.exe manage.py check --database default
.\.venv\Scripts\python.exe manage.py shell -c "from django.db import connection; c=connection.cursor(); c.execute('SELECT DATABASE(), VERSION()'); print(c.fetchone())"
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py showmigrations
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py migrate --check
```

La conexión debe imprimir voluntariados y la versión de tu MariaDB. showmigrations
debe mostrar [X], incluyendo comunidad.0001_initial. En phpMyAdmin, selecciona
voluntariados y actualiza **Estructura**: verás comunidad_actividad,
comunidad_inscripcion, comunidad_perfil, comunidad_eventoauditoria, etc.
`comunidad_incidencia` es una tabla DENTRO de voluntariados: no es la base incidencias.

## 5. Crear cuentas y abrir la API

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py crear_demo --administrador TU_USUARIO
.\.venv\Scripts\python.exe manage.py runserver --insecure
```

Reemplaza TU_USUARIO por el superusuario que acabas de crear. El comando demo pide
una contraseña para coordinador_demo y voluntario_demo. runserver ocupa la terminal;
para detenerlo usa Ctrl+C. --insecure sirve estilos con DEBUG=False solo localmente.
Abre http://127.0.0.1:8000/api-auth/login/ e inicia sesión. Luego /api/ muestra las rutas.

## 6. Verificar CRUD y reglas

En Postman, usa Basic Auth con el superusuario y Body → raw → JSON. Para comprobar
los seis métodos, usa las rutas y cuerpos de la tabla **Ejemplo de CRUD** del README.
Empieza con POST http://127.0.0.1:8000/api/categorias/ y guarda el id devuelto.
Realiza GET lista, GET detalle, PUT, PATCH y DELETE. Espera 201, 200, 200, 200, 200,
204 respectivamente; un GET posterior al borrado debe devolver 404.

Cambia a voluntario_demo: POST /api/inscripciones/ con el id real de actividad.
Repetirlo debe devolver 400. PATCH con estado cancelada conserva el registro.
Como coordinador_demo, consulta /api/actividades/indicadores/ y /api/auditoria/.
El voluntario debe recibir 403 al consultar auditoría.

Para ejecutar toda la suite, en phpMyAdmin como administrador ejecuta el contenido
de scripts/permisos_pruebas.sql. Este paso concede permisos ADICIONALES solo sobre
la base desechable test_voluntariados. Luego en otra terminal dentro del proyecto:

```powershell
.\.venv\Scripts\python.exe manage.py test --noinput -v 2
```

Django crea y elimina test_voluntariados. No guardes datos manuales en esa base.
No cambies su nombre por voluntariados ni incidencias. Las pruebas incluyen bloqueos
concurrentes para cupos y recursos, que SQLite no puede certificar.

## Errores frecuentes

- Access denied: revisa usuario, contraseña, host y permisos. No uses root en .env.
- Cannot connect / 2002 / 2003: inicia MySQL en XAMPP y revisa DB_PORT.
- Unknown database: ejecuta el SQL de creación antes de migrate.
- MariaDB 10.5 or later is required: estás ejecutando otro Python/Django; usa
  .venv/Scripts/python.exe e instala los requirements actualizados.
- Error al instalar mysqlclient: usa Python 3.12 de 64 bits. Conserva el mensaje
  completo para revisar si falta una rueda compatible o herramientas de compilación.
- Una lista de la API puede estar vacía por permisos; prueba primero como superusuario.

## Evidencias que debes enviar para confirmar tu instalación

1. phpMyAdmin: versión del servidor y Estructura de voluntariados, sin contraseñas.
2. Terminal: resultado de SELECT DATABASE(), VERSION() y showmigrations.
3. Resumen final de manage.py test.
4. Respuesta 201 de POST y 204 de DELETE en Postman o la API navegable.

Con esas capturas se puede verificar el equipo de entrega; sin ellas no se afirma
que las migraciones o las pruebas se ejecutaron en tu computador.

## Compatibilidad documentada

- https://docs.djangoproject.com/en/4.2/ref/databases/ (MariaDB 10.4+).
- https://docs.djangoproject.com/en/5.2/ref/databases/ (MariaDB 10.5+).
- https://www.djangoproject.com/weblog/2026/apr/07/security-releases/
  (fin de soporte de Django 4.2). Esta ruta sirve para la entrega local en tu motor
  actual; un despliegue público requiere actualizar la pila y volver a verificarla.
