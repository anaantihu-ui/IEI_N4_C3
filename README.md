# BiblioHub

Proyecto de Programación Backend, evaluación 2. API REST para gestionar bibliotecas, libros, ejemplares, lectores y préstamos.

Basado en el [proyecto del profesor Erick Bailey](https://github.com/baileytorch/IEI_N4_C1/tree/e030c19cc67fb7a97a0c0b24371235f3868dc277). Incluye 18 modelos y operaciones CRUD con Django REST Framework.

## Instalación

Necesitas Python 3.11 o 3.12, Git y MySQL 8 o MariaDB 10.5 o superior.

En PowerShell:

```powershell
git clone https://github.com/anaantihu-ui/IEI_N4_C3.git
cd IEI_N4_C3
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si ya tienes el proyecto, actualízalo con `git pull`.

## Base de datos y variables de entorno

Para la demostración local, inicia MySQL y ejecuta `crear_base_datos.sql` como
administrador desde phpMyAdmin o el cliente MySQL. El script y `.env` usan la
base `incidencias`, usuario `bibliohub_app`, contraseña pública de demostración
`bibliohub_pass2026`, host `127.0.0.1` y puerto `3306`.

El script crea la base y los usuarios para `localhost` y `127.0.0.1`, y concede
permisos sobre esa base. Al repetirlo restablece la contraseña de esos usuarios.
**Las tablas las crea Django al ejecutar `python manage.py migrate`**, a partir de
`biblio_app/models.py` y `biblio_app/migrations/0001_initial.py`.

Se incluye `.env` porque la consigna pide entregarlo. Sus valores son públicos y
exclusivos de una demostración local sin datos reales. `.env.example` contiene la
misma configuración. `settings.py` lee las claves desde el entorno; no las escribe
directamente en el código.

Para usar claves privadas, copia `.env.example` a `.env.local` y el SQL a
`crear_base_datos_local.sql`. Cambia la contraseña en ambas copias y genera una
clave Django con:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Guárdala como `DJANGO_SECRET_KEY` en `.env.local`. Ambos archivos privados están
excluidos de Git. Las variables del sistema tienen prioridad; si existe
`.env.local`, se lee ese archivo en lugar de `.env`. Si conservas una copia antigua,
actualiza sus valores: hacer `git pull` no modifica tus credenciales locales.

MySQL es el motor predeterminado. SQLite solo se usa al seleccionar explícitamente
`DB_ENGINE=sqlite`; no se cambia de base automáticamente si MySQL falla.

## Ejecutar

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre http://127.0.0.1:8000/api/ e inicia sesión en http://127.0.0.1:8000/api-auth/login/ con la cuenta creada. El administrador está en http://127.0.0.1:8000/admin/.

## API

Los 18 recursos están disponibles bajo `/api/`:

`paises`, `regiones`, `provincias`, `comunas`, `direcciones`, `bibliotecas`, `autores`, `generos`, `subgeneros`, `editoriales`, `idiomas`, `ediciones`, `libros`, `estados`, `ubicaciones`, `inventarios`, `usuarios` y `prestamos`.

| Método | Ejemplo | Operación |
|---|---|---|
| GET | /api/paises/ | Listar |
| POST | /api/paises/ | Crear |
| GET | /api/paises/1/ | Consultar |
| PUT | /api/paises/1/ | Actualizar todos los campos requeridos |
| PATCH | /api/paises/1/ | Actualizar algunos campos |
| DELETE | /api/paises/1/ | Eliminar |

Ejemplo de JSON para crear un país:

```json
{"nombre":"Chile","nacionalidad":"Chilena","iso_2":"CL","iso_3":"CHL","habilitado":true}
```

En Postman usa Basic Auth con tu cuenta Django. Las relaciones se envían con el ID del registro relacionado. El campo `libro` de un préstamo corresponde a un ejemplar de Inventario.

Todas las cuentas autenticadas pueden usar el CRUD. Los lectores del modelo Usuario son distintos de las cuentas Django. Sus contraseñas se guardan con hash y no aparecen en las respuestas. El borrado en cascada puede eliminar registros relacionados; usa datos de prueba. No se incluye control automático de disponibilidad ni multas.

## Pruebas y verificación

Antes de ejecutar pruebas con MySQL, aplica también `scripts/permisos_pruebas.sql`
como administrador. Autoriza al usuario de aplicación a crear y eliminar únicamente
la base de pruebas `test_incidencias`, separada de `incidencias`. No requiere permisos
globales. Si cambias `DB_TEST_NAME`, ajusta también ese script.

```powershell
python scripts/verificar_entrega.py
python manage.py check --database default
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test --noinput
```

Para probar con SQLite en PowerShell:

```powershell
$env:DB_ENGINE="sqlite"
python manage.py test --noinput
Remove-Item Env:DB_ENGINE
```

La suite incluye 25 pruebas: CRUD de las 18 entidades (GET de lista y detalle,
POST, PUT, PATCH y DELETE), autenticación, inicio de sesión, validaciones,
contraseñas de lectores y páginas existentes. Los avisos sobre comentarios de
tablas en SQLite son una limitación de ese motor.

El 31 de octubre de 2026 se verificaron las migraciones y las 25 pruebas con
MySQL 8.0.46 y, por separado, las 25 pruebas con SQLite: ambas ejecuciones
terminaron en `OK`. También se comprobó el CRUD de países por HTTP contra MySQL.

Consulta los resultados y el alcance de la comprobación en
[docs/VERIFICACION.md](docs/VERIFICACION.md). Para la evaluación debes mostrar
además el funcionamiento en tu equipo y responder las cinco preguntas individuales.

## Evidencias para presentar

1. Ejecuta los comandos anteriores y conserva las salidas de migraciones y pruebas.
2. Inicia sesión en `/api-auth/login/` y abre `/api/paises/`.
3. Crea el país del ejemplo mediante POST (201) y anota el identificador devuelto.
4. Consulta la lista y `/api/paises/ID/` con GET (200).
5. Modifica ese registro con PUT o PATCH (200).
6. Elimina el registro con DELETE (204) y comprueba que GET devuelve 404.
7. Muestra los modelos, serializers, ViewSet, Router y lectura de variables en
   `settings.py`, sin mostrar credenciales privadas.
8. Entrega la URL de GitHub y el identificador del commit que estás presentando.

En Postman puedes ejecutar PUT, PATCH y DELETE con Basic Auth. El navegador de
DRF también permite operar los recursos autenticados. Una captura de un POST por
sí sola no demuestra el CRUD completo.

El modelo está en `biblio_app/models.py`; los serializers, vistas y rutas están en
esa misma app. Hay cinco preguntas de repaso en `GUIA_DEFENSA.md`.

## Problemas frecuentes

- **Access denied:** comprueba `.env.local` y las variables del sistema; deben usar
  la misma contraseña que el SQL. Ejecuta el SQL de demostración solo en tu entorno local.
- **Can't connect:** comprueba que MySQL esté iniciado y que el host y puerto coincidan.
- **Permission denied al crear test_incidencias:** aplica `scripts/permisos_pruebas.sql`.
- **Error al instalar mysqlclient en Ubuntu:** instala previamente
  `python3-dev default-libmysqlclient-dev build-essential pkg-config`.
- **Acceso remoto o Codespaces:** configura el host concreto en `DJANGO_ALLOWED_HOSTS`
  y su origen HTTPS en `DJANGO_CSRF_TRUSTED_ORIGINS`, separados por comas si son varios.
  Localmente no es necesario configurar orígenes adicionales.
