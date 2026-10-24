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
Copy-Item .env.example .env.local
```

Si ya tienes el proyecto, actualízalo con `git pull`.

## Base de datos

1. Copia `crear_base_datos.sql` como `crear_base_datos_local.sql`.
2. Reemplaza la contraseña de ejemplo en esa copia y ejecuta el SQL desde phpMyAdmin con una cuenta administradora.
3. Edita `.env.local` con esa misma contraseña. La base es `incidencias`, el usuario `bibliohub_app` y el host `127.0.0.1`. Mantén `DB_ENGINE=mysql`.
4. Genera una clave y guárdala como `DJANGO_SECRET_KEY` en `.env.local`:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Los archivos `.env` y `.env.example` contienen solo valores de ejemplo. Las credenciales reales se guardan en `.env.local`, que está excluido de Git.

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

## Pruebas

Para ejecutar las pruebas con SQLite en PowerShell:

```powershell
$env:DB_ENGINE="sqlite"
python manage.py test
Remove-Item Env:DB_ENGINE
```

Las 24 pruebas pasan con SQLite. Los avisos sobre comentarios de tablas son una limitación de SQLite. Falta comprobar el SQL, las migraciones y el CRUD con MySQL en el equipo de entrega.

El modelo está en `biblio_app/models.py`; los serializers, vistas y rutas están en esa misma app. Hay cinco preguntas de repaso en `GUIA_DEFENSA.md`.
