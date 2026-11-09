# Plataforma de Voluntariados y Actividades Comunitarias

Proyecto de Programación Backend: API REST para organizaciones sociales, actividades,
voluntarios, coordinadores, inscripciones, asistencia, recursos e incidencias.
Desarrollado con Django y Django REST Framework, mediante ModelViewSet y Router.
Incluye historial de cambios, permisos por organización, filtros e indicadores.

## Obtener esta implementación

```powershell
git clone --branch implementacion/voluntariados https://github.com/anaantihu-ui/IEI_N4_C3.git
cd IEI_N4_C3
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Requisitos: Python 3.11 o 3.12 y MySQL 8.0. En Ubuntu, antes de instalar las
librerías Python: `sudo apt install python3-venv python3-dev default-libmysqlclient-dev build-essential pkg-config`.

## Base de datos y entorno

1. Inicia MySQL y ejecuta `crear_base_datos.sql` como administrador, por ejemplo
   desde la pestaña SQL de phpMyAdmin. El script crea la base `voluntariados`,
   el usuario `voluntariados_app` y sus permisos para localhost y 127.0.0.1.
2. El `.env` entregado ya coincide con el script: conexión TCP a 127.0.0.1:3306.
   Los valores son públicos y sirven exclusivamente para una demostración local.
3. Las tablas se crean con Django:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre http://127.0.0.1:8000/api-auth/login/ e ingresa con tu superusuario. Después
abre http://127.0.0.1:8000/api/. No se requieren formularios HTML propios.

La consigna exige incluir `.env`. Para datos privados, copia `.env.example` a
`.env.local` y el SQL a `crear_base_datos_local.sql`; cambia las contraseñas en
ambos archivos. Están excluidos de Git. Genera tu propia `DJANGO_SECRET_KEY` con:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

`settings.py` lee las claves con python-decouple. Las variables del sistema tienen
prioridad; si existe `.env.local`, reemplaza la lectura de `.env`. Una copia local
antigua puede apuntar a otra base: revísala al actualizar el proyecto.

El SQL restablece la clave de los usuarios de demostración si se ejecuta otra vez.
Las tablas y datos de la antigua biblioteca no se usan: esta implementación utiliza
una base nueva. No hay cambio automático a SQLite si falla MySQL.

## Datos para practicar

Con las migraciones aplicadas y tu superusuario creado:

```powershell
python manage.py crear_demo --administrador TU_NOMBRE_DE_SUPERUSUARIO
```

El comando pide una contraseña para `coordinador_demo` y `voluntario_demo`. Crea
una organización ficticia de Temuco, categoría, ubicación, actividad futura y recurso.
Al repetirlo conserva las cuentas y registros existentes; no cambia sus contraseñas.
Para ejecución automatizada se puede usar `DEMO_PASSWORD` y `--noinput`.
No carga información real. Si la actividad demo ya pasó, crea una nueva por la API.

## Endpoints y permisos

Cada entidad operativa tiene GET de lista/detalle, POST, PUT, PATCH y DELETE.
Los permisos y las reglas de integridad pueden rechazar una operación; el CRUD
no autoriza a borrar registros históricos con dependencias.

| Ruta bajo `/api/` | Quién consulta | Quién modifica |
|---|---|---|
| `organizaciones/` | Público: organizaciones activas | Administrador |
| `categorias/` | Público | Administrador |
| `perfiles/` | Administrador o el propio titular | Administrador crea/elimina; titular actualiza sus datos y contraseña |
| `ubicaciones/` | Administrador y coordinador de la organización | Administrador y coordinador de la organización |
| `actividades/` | Público: publicadas y públicas; miembros: internas; coordinador: sus borradores | Administrador y coordinador de la organización |
| `inscripciones/` | Administrador, coordinador de la actividad o voluntario titular | Los mismos, según las reglas de inscripción |
| `asistencias/` | Administrador, coordinador de la actividad o voluntario titular | Administrador y coordinador de la actividad |
| `recursos/` | Administrador y coordinador de la organización | Los mismos |
| `asignaciones/` | Administrador y coordinador de la actividad | Los mismos |
| `incidencias/` | Administrador, coordinador de la actividad o reportante | Participante reporta; coordinador gestiona resolución |
| `auditoria/` | Administrador; coordinador consulta su organización, sin historiales de perfiles | Solo lectura; generación automática |

Administrador significa una cuenta Django con `is_superuser=True`. Los demás
roles están en `Perfil`. El administrador crea cuentas mediante `/api/perfiles/`,
con `username`, `password`, `rol` y, para coordinadores, `organizacion`.
Las contraseñas usan el hash de Django y no aparecen en respuestas ni auditorías.
La API no expone un campo para convertir una cuenta en superusuario.

En Postman usa Basic Auth con una cuenta Django; en el navegador usa la sesión
iniciada en `/api-auth/login/`. Fuera del entorno local debe utilizarse HTTPS.
El administrador Django permite inspeccionar entidades del dominio; sus escrituras
se realizan por la API para conservar validaciones y auditoría.

## Ejemplo de CRUD

Con el superusuario, crea una categoría que todavía no use ninguna actividad:

```http
POST /api/categorias/
Content-Type: application/json

{"nombre":"Apoyo educativo","descripcion":"Actividades de aprendizaje"}
```

La respuesta 201 devuelve un `id`. Usando ese identificador:

| Método y ruta | Cuerpo | Resultado esperado |
|---|---|---|
| GET `/api/categorias/` | Sin cuerpo | 200, lista paginada |
| GET `/api/categorias/ID/` | Sin cuerpo | 200, detalle |
| PUT `/api/categorias/ID/` | `{"nombre":"Educación comunitaria","descripcion":"Descripción completa"}` | 200 |
| PATCH `/api/categorias/ID/` | `{"descripcion":"Descripción corregida"}` | 200 |
| DELETE `/api/categorias/ID/` | Sin cuerpo | 204 si no tiene dependencias |
| GET `/api/categorias/ID/` | Sin cuerpo, después del borrado | 404 |

Para inscribirte con `voluntario_demo`, consulta `/api/actividades/` y envía:

```json
{"actividad": 1}
```

A `/api/inscripciones/`. Reemplaza 1 por el ID real; el voluntario se infiere de la
sesión. Para cancelar antes del inicio: PATCH `/api/inscripciones/ID/` con
`{"estado":"cancelada"}`. Repetir el POST no crea una inscripción duplicada.

## Búsquedas e indicadores

- `/api/actividades/?search=Temuco&estado=publicada&ordering=inicio`
- `/api/actividades/?organizacion=1&categoria=1&desde=2026-12-01T00:00:00Z&hasta=2027-01-01T00:00:00Z`
- `/api/actividades/indicadores/` (administrador o coordinador).
- `/api/auditoria/?entidad=actividad&objeto_id=1`

Las listas se paginan en bloques de 50; usa `?page=2`. Los indicadores incluyen
actividad por estado, inscripciones recientes y por mes, voluntarios distintos,
asistencias, horas, ocupación, recursos en uso e incidencias pendientes. Los filtros
aplicados a actividades delimitan también los indicadores. Un coordinador solo
obtiene indicadores de su propia organización.

## Validación y pruebas

Para MySQL, ejecuta también `scripts/permisos_pruebas.sql` como administrador.
Autoriza la creación y eliminación de `test_voluntariados`, separada de la base
normal. No concede permisos globales. Luego:

```powershell
python scripts/verificar_entrega.py
python manage.py check --database default
python manage.py makemigrations --check --dry-run
python manage.py migrate --check
python manage.py test --noinput -v 2
```

Alternativa SQLite, seleccionada explícitamente:

```powershell
$env:DB_ENGINE="sqlite"
python manage.py migrate
python manage.py test --noinput -v 2
Remove-Item Env:DB_ENGINE
```

Las pruebas concurrentes requieren MySQL porque SQLite no ofrece los mismos
bloqueos de filas. Consulta los resultados reales en [docs/VERIFICACION.md](docs/VERIFICACION.md).

## Archivos para la evaluación

- Modelo y migración: `comunidad/models.py`, `comunidad/migrations/0001_initial.py`.
- API: `comunidad/serializers.py`, `comunidad/views.py`, `comunidad/urls.py`, `drf/urls.py`.
- Conexión: `crear_base_datos.sql`, `.env`, `drf/settings.py`.
- Reglas y diseño: [docs/MODELO_Y_REGLAS.md](docs/MODELO_Y_REGLAS.md).
- Preguntas de preparación: [GUIA_DEFENSA.md](GUIA_DEFENSA.md).

Entrega el enlace de la rama que contiene esta implementación y su commit, o
integra el PR antes de entregar el enlace de `main`. Demuestra las operaciones
por API en tu equipo y responde las cinco preguntas individuales.
