# BiblioHub — Evaluación 2 de Programación Backend

API REST educativa con Django y Django REST Framework. Implementa 18 entidades, migraciones, serializers, ModelViewSet y DefaultRouter con GET, POST, PUT, PATCH y DELETE.

## Procedencia y alcance

El modelo se adapta del ejemplo del docente Erick Bailey Rebolledo:
https://github.com/baileytorch/IEI_N4_C1/tree/e030c19cc67fb7a97a0c0b24371235f3868dc277

Se conservan sus entidades, campos y relaciones. La app `biblio_app` es nueva en este repositorio: por eso tiene una migración inicial propia. Se conservan las apps y páginas originales (`mi_app`, `incidencias`) y el proyecto de configuración `drf`.

Esta entrega implementa el CRUD del modelo. No añade gestión automática de stock, multas, reservas ni disponibilidad de ejemplares. Los borrados mantienen el comportamiento CASCADE del ejemplo docente: borrar un registro padre puede borrar registros dependientes. Utiliza datos de prueba al demostrar DELETE.

## Modelo y endpoints

Todos los endpoints requieren iniciar sesión. La raíz es `/api/`.

| Modelo | Endpoint | Relaciones directas |
|---|---|---|
| Pais | paises | — |
| Region | regiones | — |
| Provincia | provincias | Region |
| Comuna | comunas | Provincia |
| Direccion | direcciones | Comuna |
| Biblioteca | bibliotecas | Direccion |
| Autor | autores | Pais (nacionalidad) |
| Genero | generos | — |
| SubGenero | subgeneros | Genero |
| Editorial | editoriales | Direccion |
| Idioma | idiomas | — |
| Edicion | ediciones | Editorial, Idioma |
| Libro | libros | Autor, SubGenero, Edicion, Biblioteca |
| Estado | estados | — |
| Ubicacion | ubicaciones | — |
| Inventario | inventarios | Libro, Estado, Ubicacion |
| Usuario | usuarios | Pais, Direccion, Biblioteca |
| Prestamo | prestamos | Inventario (campo libro), Usuario (campo lector) |

Las relaciones se envían como IDs existentes. `id`, `created_at`, `updated_at` y `fecha_prestamo` son gestionados por Django. `Usuario` representa un lector, no una cuenta de acceso a la API. Para autenticarse se usan las cuentas de Django creadas con `createsuperuser` o desde el administrador. `contrasenia` del lector se guarda con hash y nunca se devuelve por la API.

## Instalación (Windows / PowerShell)

Requisitos: Python 3.11 o 3.12, Git y MySQL 8 o MariaDB 10.5 o superior compatible con Django 5.2. Un XAMPP con MariaDB 10.4 requiere actualizar el servidor.

```powershell
git clone https://github.com/anaantihu-ui/IEI_N4_C3.git
cd IEI_N4_C3
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env.local
```

Si ya tienes el proyecto, actualiza con `git pull` antes de instalar. Si `mysqlclient` no tiene una rueda compatible con tu Python, requiere herramientas de compilación y las bibliotecas cliente MySQL/MariaDB. En Linux se necesitan también `pkg-config` y cabeceras de desarrollo. No reemplaces MySQL por SQLite como evidencia de conexión MySQL.

Edita `.env.local`: genera una clave privada para `DJANGO_SECRET_KEY` y configura `DB_PASSWORD`. Para generar la clave:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

`.env` y `.env.example` son plantillas públicas con marcadores; no contienen credenciales operativas. `.env.local` está excluido de Git. Las variables del sistema tienen prioridad sobre el archivo. Mantén `DB_ENGINE=mysql` para la entrega MySQL.

## Crear base, usuario y permisos

1. Copia `crear_base_datos.sql` como `crear_base_datos_local.sql`.
2. Cambia el marcador de contraseña solo en esa copia privada.
3. Ejecuta el SQL con una cuenta administradora en phpMyAdmin o en el cliente MySQL.
4. Comprueba que exista la base **incidencias**, el usuario **bibliohub_app** y sus permisos. No uses la base interna `mysql` como base del proyecto.
5. Configura los mismos datos en `.env.local`, incluido `DB_HOST=127.0.0.1`.

El nombre de la base `incidencias` se conserva por compatibilidad con la configuración anterior. Puede almacenar las tablas de BiblioHub. `CREATE USER IF NOT EXISTS` no cambia la contraseña de un usuario ya existente: si ya existía, comprueba sus credenciales con el administrador.

```powershell
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre http://127.0.0.1:8000/api/ y utiliza el enlace de inicio de sesión de la API (http://127.0.0.1:8000/api-auth/login/). El administrador está en `/admin/`. Sin autenticación los recursos responden 401. Todos los usuarios autenticados pueden gestionar el catálogo: esta es una política académica, no roles de producción. Basic Authentication se ofrece para pruebas locales; cualquier despliegue remoto debe utilizar HTTPS y configuración de producción.

## Demostrar el CRUD

Ejemplo con `/api/paises/`, después de iniciar sesión:

| Método | URL | Efecto y respuesta |
|---|---|---|
| GET | /api/paises/ | Lista, 200 |
| POST | /api/paises/ | Crea, 201 |
| GET | /api/paises/ID/ | Consulta un registro, 200 |
| PUT | /api/paises/ID/ | Actualización completa, 200 |
| PATCH | /api/paises/ID/ | Actualización parcial, 200 |
| DELETE | /api/paises/ID/ | Eliminación, 204 |

POST o PUT (reemplaza ID por el identificador devuelto):

```json
{"nombre":"Chile","nacionalidad":"Chilena","iso_2":"CL","iso_3":"CHL","habilitado":true}
```

PATCH:

```json
{"nombre":"Chile actualizado"}
```

En Postman selecciona Basic Auth e ingresa tu cuenta Django. Usa Body → raw → JSON para POST, PUT y PATCH. La API devuelve 400 ante datos inválidos y 404 para IDs inexistentes. Primero crea los catálogos y luego las entidades dependientes, siguiendo la tabla del modelo. Las páginas de libros deben ser positivas y las fechas de devolución/retorno no pueden ser anteriores al préstamo.

## Verificación

```powershell
python scripts/verificar_entrega.py
python manage.py makemigrations --check --dry-run
python manage.py showmigrations biblio_app
```

El verificador requiere Git y revisa archivos y exclusiones, no conexión ni credenciales de MySQL. En una entrega no debe incluirse `.env.local`.

Para pruebas aisladas con SQLite (PowerShell):

```powershell
$env:DB_ENGINE="sqlite"
python manage.py test
Remove-Item Env:DB_ENGINE
```

Las 24 pruebas incluyen CRUD con persistencia para los 18 endpoints, acceso anónimo, autenticación, hash de contraseñas, datos inválidos y las dos páginas originales. SQLite advierte que no soporta comentarios de tablas; esto no impide ejecutar las pruebas. Las pruebas MySQL necesitan una cuenta de pruebas con permisos para crear y borrar una base de pruebas; no amplíes por ello los permisos del usuario de ejecución normal.

**Validado en el entorno de desarrollo:** CRUD y migraciones con SQLite. **Pendiente en el equipo de entrega:** instalación completa de mysqlclient, ejecución SQL y migraciones/conexión real MySQL. Guarda evidencia de `migrate`, `showmigrations`, tablas en phpMyAdmin y peticiones CRUD sobre MySQL antes de afirmar que la persistencia MySQL está verificada.

## Archivos y defensa

- `biblio_app/models.py`, `migrations/`: modelo y esquema.
- `biblio_app/serializers.py`: JSON, validaciones y protección de contraseñas.
- `biblio_app/views.py`, `urls.py`: ModelViewSet y Router.
- `crear_base_datos.sql`, `.env`, `.env.example`: configuración de entrega.
- `GUIA_DEFENSA.md`: cinco preguntas explicadas.
- `VERIFICACION_Y_CAMBIOS.md`: alcance de las comprobaciones.

Repositorio de entrega: https://github.com/anaantihu-ui/IEI_N4_C3
