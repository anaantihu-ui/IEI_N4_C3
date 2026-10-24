# IEI_N4_C3 — Proyecto Django de clases

Proyecto Django educativo con una página de bienvenida, una página personalizada para el error 404 y aplicaciones llamadas `mi_app` e `incidencias`.

> **Estado comprobado en el ZIP recibido:** los archivos `models.py` de ambas aplicaciones no definen modelos de negocio; no se encontraron serializers ni endpoints REST bibliotecarios. Por tanto, **esta versión no es un BiblioHub de gestión bibliotecaria completo**. Esta entrega mejora la **configuración y documentación**, sin atribuirle funciones inexistentes.

## Contenido

- `manage.py`: comandos de administración de Django.
- `drf/settings.py`: configuración de seguridad, apps y bases de datos por variables de entorno.
- `drf/urls.py`: rutas `/` (bienvenida) y `/admin/`; manejador 404 personalizado.
- `mi_app/`: vistas y plantillas de bienvenida y error 404.
- `incidencias/`: aplicación Django registrada, actualmente sin modelos de negocio.
- `crear_base_datos.sql`: creación de BD MySQL, usuario dedicado y permisos.
- `.env`: **solo marcadores públicos**, por petición académica.
- `.env.example`: plantilla de configuración.
- `.gitignore`: protege `.env.local`, entornos, cachés y SQLite local.
- `requirements.txt`: dependencias de Django, python-decouple y mysqlclient.
- `scripts/verificar_entrega.py`: revisión de archivos y reglas de entrega.
- `GUIA_DEFENSA.md`: explicación de los conceptos principales para exposición oral.

## Requisitos

- Python 3.11 o una versión compatible con los paquetes indicados.
- MySQL compatible con Django 5.2, o MariaDB **10.5 o superior**; verificar la compatibilidad de la versión exacta usada.
- Windows: XAMPP solo si su versión de MariaDB es compatible; en algunas instalaciones antiguas incluye MariaDB 10.4, que **no es compatible** con esta versión de Django.

## Instalación en Windows / PowerShell

Desde la carpeta del proyecto, donde está `manage.py`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si tu instalación no puede compilar `mysqlclient`, instala el conector siguiendo las instrucciones de la versión compatible para Windows/Python antes de continuar.

### Configuración local (credenciales fuera de GitHub)

**El `.env` versionado NO contiene credenciales operativas:** está preparado solo para la revisión pública del profesor.

1. Copia `.env` como `.env.local` en el mismo directorio que `manage.py`.
2. Edita **solo** `.env.local`: sustituye `DJANGO_SECRET_KEY` por una clave generada de forma segura y cambia `DB_PASSWORD` por una contraseña privada.
3. Mantén `.env.local` fuera de GitHub (`.gitignore` ya lo excluye).
4. Si trabajas con MySQL, asegúrate de que el usuario, host, contraseña y BD coincidan con `crear_base_datos.sql`.
5. Las variables de entorno del sistema pueden sobrescribir valores de ese archivo.

Por ejemplo, para crear una clave secreta en PowerShell (con Python y Django instalados):

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Preparar la base MySQL

1. Inicia el servidor MySQL o MariaDB compatible.
2. Haz una copia de `crear_base_datos.sql` llamada `crear_base_datos_local.sql` y cambia **solo en esa copia local** `REEMPLAZAR_CON_PASSWORD_LOCAL` por una contraseña privada. Ese archivo está excluido en `.gitignore`.
3. Ejecuta `crear_base_datos_local.sql` con una cuenta administradora desde phpMyAdmin (pestaña SQL/Importar) o el cliente `mysql`.
4. Copia la misma contraseña en el `DB_PASSWORD` de `.env.local`.
5. Ejecuta:

```powershell
python manage.py check
python manage.py migrate
python manage.py test
python manage.py runserver
```

Abre <http://127.0.0.1:8000/>. El usuario de la base se creó con el host `127.0.0.1`, por lo que la configuración debe usar el mismo host.

**Importante:** `migrate` crea o actualiza la *estructura* de tablas; no importa datos previamente guardados en `db.sqlite3`. Si necesitas trasladar datos, hace falta un procedimiento adicional.

### Pruebas sin MySQL (SQLite solo para validación local)

Cambia `DB_ENGINE=sqlite` **solo en `.env.local`** y ejecuta:

```powershell
python manage.py check
python manage.py migrate
python manage.py test
```

Es una alternativa temporal para comprobar las páginas y migraciones, **no** una prueba de conectividad con MySQL.

## Requisitos de entrega del profesor

- [x] URL de un repositorio público (inclúyela en la plataforma de entrega).
- [x] Script SQL con creación de BD, usuario y permisos.
- [x] Archivo `.env` publicable con **marcadores**, sin credenciales reales.
- [x] `.gitignore` permite versionar `.env` y excluye `.env.local`.
- [ ] Verificar MySQL funcionando en el equipo de entrega.
- [ ] Comprobar subida de los archivos a GitHub y que el repositorio sea público.

**Repositorio a utilizar:** <https://github.com/anaantihu-ui/IEI_N4_C3>

## Cómo subir los cambios

Desde una copia del proyecto bajo Git (o clonando tu repositorio):

```powershell
git status
git add .
git status
git commit -m "Agregar SQL, configuracion segura y documentacion"
git push origin main
```

Revisa siempre `git status` antes de `git add .` para evitar incluir secretos. El ZIP entregado está limpio: no contiene `.git`, bases locales ni entornos virtuales.
