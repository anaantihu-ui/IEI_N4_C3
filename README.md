# IEI_N4_C3 — Plataforma de Voluntariados y Actividades Comunitarias

Proyecto académico de Programación Backend desarrollado con **Python, Django y Django REST Framework**. Permite definir y consultar datos de organizaciones, actividades comunitarias, voluntarios, inscripciones y recursos a través de una API REST.

## Funcionalidades implementadas

El archivo **mi_app/models.py** contiene 13 modelos: Region, Comuna, Perfil, Organizacion, Categoria, Estado, Voluntario, Coordinador, Actividad, Inscripcion, Recurso, AsignacionRecurso e HistorialEstado.

Cada uno cuenta con un **ModelSerializer** en **mi_app/serializer.py** y un **ModelViewSet** en **mi_app/views.py**. Las rutas se generan con **DefaultRouter** en **mi_app/urls.py**. Las vistas HTML de bienvenida y error 404 se mantienen.

### Recursos de la API

Las rutas se encuentran bajo **/api/**:

| Recurso | Ruta |
| --- | --- |
| Regiones | /api/regiones/ |
| Comunas | /api/comunas/ |
| Perfiles | /api/perfiles/ |
| Organizaciones | /api/organizaciones/ |
| Categorías | /api/categorias/ |
| Estados | /api/estados/ |
| Voluntarios | /api/voluntarios/ |
| Coordinadores | /api/coordinadores/ |
| Actividades | /api/actividades/ |
| Inscripciones | /api/inscripciones/ |
| Recursos | /api/recursos/ |
| Asignaciones | /api/asignaciones/ |
| Historial de estados | /api/historial/ |

Los ModelViewSet proporcionan operaciones CRUD: GET (lista/detalle), POST (creación), PUT/PATCH (actualización) y DELETE (eliminación), sujetas a los datos y configuraciones disponibles. **No se ha realizado una prueba de integración de todos estos endpoints con MySQL**.

## Archivos importantes

- **manage.py:** comandos de administración de Django.
- **drf/settings.py:** aplicaciones, configuración, variables de entorno y base de datos.
- **drf/urls.py:** rutas principales de la aplicación.
- **mi_app/models.py:** estructura de las 13 entidades.
- **mi_app/serializer.py:** serializadores de la API.
- **mi_app/views.py:** vistas y ModelViewSet.
- **mi_app/urls.py:** registro del router REST.
- **mi_app/migrations/0001_initial.py:** migración inicial de los 13 modelos.
- **sql.sql:** creación de la base de datos, usuario y permisos de MySQL.
- **.env:** plantilla pública exigida para la evaluación, sin secretos reales.
- **.env.example:** copia de la plantilla para facilitar la configuración.
- **.gitignore:** excluye entornos virtuales, archivos temporales y configuraciones privadas.

## Requisitos

- Python compatible con Django 5.2 (por ejemplo, Python 3.11).
- Paquetes en **requirements.txt** (incluye django, djangorestframework, python-decouple y mysqlclient).
- Para MySQL: servidor MySQL 8.0.11+ o MariaDB 10.5+; algunas instalaciones antiguas de XAMPP incluyen MariaDB 10.4, incompatible con Django 5.2.
- Una cuenta administradora de MySQL para ejecutar **sql.sql**.

## Instalación en Windows (PowerShell)

En la carpeta raíz donde está **manage.py**:

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
~~~

### 1. Crear base de datos y usuario

Abra **sql.sql** y reemplace **CAMBIAR_CLAVE_MYSQL_EN_EQUIPO** por una contraseña fuerte **en una copia local que NO subirá a GitHub**. Ejecute las sentencias desde phpMyAdmin (SQL) o el cliente MySQL con permisos de administración.

El script crea la base **voluntariados**, el usuario **vol_app@localhost** y asigna permisos para operar y aplicar migraciones. No crea manualmente las tablas de los modelos: Django lo hace con **migrate**.

Si MySQL ya tiene creado ese usuario con otra clave, configure la contraseña con ALTER USER en una sesión privada. Compruebe la versión del servidor con SELECT VERSION();.

### 2. Configurar las variables locales sin publicar secretos

La pauta exige publicar **.env**, por lo que ese archivo contiene solo valores de ejemplo. Para ejecutar Django, sobrescriba los valores en la terminal (python-decouple prioriza las variables del sistema sobre las de .env).

~~~powershell
$env:SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
$env:DB_PASSWORD = "TU_CONTRASENA_LOCAL_DE_MYSQL"
$env:DB_ENGINE = "mysql"
$env:DEBUG = "True"
~~~

La contraseña indicada debe ser exactamente la que asignó al usuario en MySQL. Las variables de PowerShell duran la sesión de esa terminal.

**Nunca publique su contraseña real ni una SECRET_KEY válida en este repositorio.** Una clave anterior publicada debe considerarse comprometida, aunque se reemplace: el historial de Git puede conservarla.

### 3. Verificar base de datos y migraciones

~~~powershell
python manage.py check
python manage.py showmigrations
python manage.py migrate
python manage.py runserver
~~~

Visite http://127.0.0.1:8000/ y http://127.0.0.1:8000/api/. Para probar recursos concretos, consulte por ejemplo http://127.0.0.1:8000/api/regiones/.

En la terminal puede ejecutar también **python manage.py test**. Actualmente no se aporta aquí evidencia de pruebas de integración completas sobre un servidor MySQL.

### Alternativa de desarrollo con SQLite

El código conserva SQLite como alternativa para trabajar sin MySQL. Antes de ejecutar Django, establezca:

~~~powershell
$env:DB_ENGINE = "sqlite"
python manage.py migrate
python manage.py runserver
~~~

Esta opción sirve para pruebas locales; **no equivale a verificar MySQL**.

## Observaciones y límites

- **sql.sql** prepara la base, el usuario y los permisos; las tablas se generan con las migraciones existentes.
- El código incluye ViewSets CRUD, pero su disponibilidad efectiva requiere servidor y base de datos operativos.
- El proyecto no está configurado como aplicación de producción: antes de publicarlo en Internet se deben gestionar DEBUG=False, ALLOWED_HOSTS, SECRET_KEY privada, autorización de API y otras medidas de seguridad.
- El cambio de SQLite a MySQL configura el motor, pero **no copia automáticamente datos preexistentes** de un archivo SQLite.
- La carpeta **incidencias** existe, pero los 13 modelos del proyecto actual están en **mi_app**, no en incidencias.

## Entrega solicitada

Entregar la URL pública de este repositorio. En su raíz figuran **sql.sql**, **.env** (plantilla pública) y **.gitignore** modificado; los cambios de base de datos pueden reproducirse mediante el SQL y las migraciones de Django.


## Interfaz web de gestión (HTML, CSS y JavaScript)

El proyecto incorpora una interfaz profesional y adaptable para demostrar el funcionamiento de la API REST sin modificar los 13 modelos ni sus migraciones.

- **/**: dashboard con indicadores obtenidos de la API y listados de actividades y voluntarios.
- **/gestion/voluntarios/**, **/gestion/actividades/**, **/gestion/organizaciones/**, **/gestion/inscripciones/** y **/gestion/recursos/**: módulos principales de administración.
- **/gestion/regiones/**, **/gestion/comunas/**, **/gestion/perfiles/**, **/gestion/categorias/**, **/gestion/estados/**, **/gestion/coordinadores/**, **/gestion/asignaciones/** y **/gestion/historial/**: catálogos y módulos complementarios.

Las tablas permiten buscar, filtrar por habilitado cuando aplica y navegar entre páginas. Los formularios crean y editan registros mediante POST/PATCH, y la eliminación exige confirmación antes de enviar DELETE. Los campos de relaciones obtienen sus opciones de otros endpoints; si todavía no existen datos relacionados, primero deben registrarse las regiones, comunas, organizaciones, etc.

Los archivos de la interfaz son:
- **mi_app/templates/base.html**: estructura general y navegación.
- **mi_app/templates/dashboard.html**: panel principal.
- **mi_app/templates/panel.html**: formulario y tabla reutilizable.
- **mi_app/static/mi_app/css/app.css**: estilos responsivos propios, sin depender de una CDN.
- **mi_app/static/mi_app/js/app.js**: consumo de la API REST y acciones CRUD.
- **mi_app/tests.py**: pruebas de rutas y renderizado de la interfaz.

**Para verla funcionando en Windows (PowerShell)**, estando en la raíz del proyecto y con las dependencias instaladas:

~~~powershell
$env:DB_ENGINE = "sqlite"
python manage.py migrate
python manage.py runserver
~~~

Abre **http://127.0.0.1:8000/** en el navegador. Las cifras y listas vienen de la base de datos real; si la base está vacía, verás ceros y estados vacíos, no datos inventados. Para usar MySQL, configura credenciales privadas y el motor conforme a las instrucciones anteriores. Prueba el renderizado de la interfaz con **python manage.py test mi_app**.

**Seguridad:** es una interfaz de demostración académica, no un sistema preparado para Internet. La API original no configura autenticación ni permisos específicos para proteger RUT, correos u otros datos personales. Antes de desplegarla públicamente deben añadirse autenticación, autorización y controles de acceso.


## Diseño personalizado del explorador web de la API

Además del dashboard, las páginas de Django REST Framework (como /api/voluntarios/) utilizan ahora el tema Comunidad+, con barra lateral, menú de recursos, encabezado y diseño profesional para las respuestas JSON y los formularios integrados.

La personalización se encuentra en **templates/rest_framework/api.html** y extiende la plantilla oficial de Django REST Framework. En **drf/settings.py** se añade BASE_DIR / 'templates' a TEMPLATES['DIRS']. Las operaciones API y las vistas originales de DRF siguen intactas; el estilo no modifica respuestas cuando se solicita el formato JSON.

### Si la pantalla sigue sin CSS

Descarga o actualiza el proyecto desde GitHub, reinicia runserver y recarga con Ctrl+F5. En desarrollo local verifica DEBUG=True, que permite servir los archivos estáticos de DRF con runserver. Ejecuta:

~~~powershell
python manage.py findstatic rest_framework/css/bootstrap.min.css
~~~

Si no se encuentra el archivo, comprueba las dependencias. Si el navegador recibe 404 al solicitar /static/rest_framework/css/bootstrap.min.css, revisa la configuración de archivos estáticos y DEBUG. El tema incluye estilos inline como respaldo, pero algunas interacciones de los formularios requieren los JavaScript estáticos de Django REST Framework.

Verifica el tema y la compatibilidad de la API con:

~~~powershell
python manage.py test mi_app.tests.TemaAPINavegableTests
~~~
