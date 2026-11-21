# Evaluación 3: formularios, CBV y templates

La aplicación del proyecto se llama **comunidad**, no mi_app. Se conserva la API
REST de la Evaluación 2 en /api/ y se incorpora la interfaz web en /web/.

## Correspondencia con los requisitos entregados

| Requisito | Implementación |
|---|---|
| forms.py | comunidad/forms.py: diez ModelForm con campos explícitos |
| ListView | Clases *ListView en comunidad/web_views.py, paginación y búsqueda |
| DetailView | Clases *DetailView, campos y acciones según perfil |
| CreateView | Clases *CreateView, validación y mensaje de creación |
| UpdateView | Clases *UpdateView, validación y mensaje de actualización |
| DeleteView | Clases *DeleteView, confirmación y borrado solo mediante POST |
| URLs web separadas | comunidad/web_urls.py, namespace web, prefijo /web/ |
| Templates CRUD | comunidad/templates/comunidad/registro_list.html, registro_detail.html, registro_form.html, registro_confirm_delete.html |
| Template base | comunidad/templates/base.html: navbar, menú, bloques y mensajes |
| Login / logout | registration/login.html, IniciarSesionView y CerrarSesionView |
| Mensajes Django | Ya estaban configurados app, middleware y context processor en drf/settings.py; ahora se muestran en base.html |
| Estilos | comunidad/static/comunidad/web.css: diseño adaptable sin dependencias externas |

Los cuatro templates CRUD se reutilizan entre entidades para no repetir el HTML.
Los ModelForm y las CBV concretas están declarados por entidad. Por ejemplo,
ActividadForm, ActividadListView, ActividadDetailView, ActividadCreateView,
ActividadUpdateView y ActividadDeleteView.

Entidades: organizaciones, perfiles (voluntarios/coordinadores), categorías,
ubicaciones, actividades, inscripciones, asistencias, recursos, asignaciones e
incidencias. La auditoría permanece de solo lectura en la API.

## Rutas de ejemplo

| Ruta | Uso |
|---|---|
| / | Redirige al listado web de actividades |
| /web/ingresar/ | Inicio de sesión propio para la web |
| /web/salir/ | Cierre de sesión mediante POST con CSRF |
| /web/actividades/ | Lista, búsqueda con ?q= y paginación con ?page= |
| /web/actividades/nuevo/ | Crear una actividad |
| /web/actividades/1/ | Ver la actividad con id 1 |
| /web/actividades/1/editar/ | Editar la actividad |
| /web/actividades/1/eliminar/ | Confirmar eliminación |
| /api/ | API REST original |

Se repite el patrón para cada entidad. Los identificadores dependen de tu base.
Todos los módulos web requieren inicio de sesión. Los permisos se comprueban en
el servidor: ocultar un botón no es la protección de seguridad.

## Flujo y reglas de negocio

1. La URL selecciona una CBV. ListView/DetailView usan el queryset visible para el
   usuario, igual que la API.
2. CreateView/UpdateView presentan un ModelForm con controles HTML y campos
   relacionados filtrados por organización o titular.
3. ModelForm valida tipos, campos obligatorios y restricciones del modelo.
4. web_services.guardar abre una transacción y bloquea las organizaciones con el
   mismo orden que la API. Recarga el registro original: is_valid() de ModelForm
   modifica su instancia en memoria y no debe borrar el estado anterior a auditar.
5. Se valida con el serializer existente y se guarda mediante los métodos del
   ViewSet, conservando cupos, fechas, estados, auditoría y cancelaciones relacionadas.
6. Los errores se presentan en el formulario sin guardar; los éxitos redirigen al
   detalle y muestran un mensaje. Esta redirección evita reenviar el POST al refrescar.
7. DeleteView no borra con GET. El POST validado ejecuta las reglas de borrado de
   la API; PROTECT o una regla histórica muestran el error y revierten la transacción.

Este adaptador no hace llamadas HTTP internas ni duplica las reglas. Los formularios
no llaman a form.save() directamente, porque saltaría la auditoría y las reglas
que ya están implementadas en los serializers/ViewSets.

Al editar actividades con inscripciones o asignaciones, las fechas aparecen
bloqueadas para conservar el historial y sus valores exactos.

## Abrir en Windows

Primero actualiza la rama implementacion/voluntariados conservando cambios locales.
Con la base y el .env.local ya configurados, desde la carpeta de manage.py:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py crear_demo --administrador TU_USUARIO
.\.venv\Scripts\python.exe manage.py runserver --insecure
```

Omite createsuperuser si ya tienes esa cuenta. Reemplaza TU_USUARIO por su nombre.
Abre http://127.0.0.1:8000/web/ingresar/. El superusuario puede gestionar todas las
entidades. Los coordinadores gestionan su organización; los voluntarios acceden a
sus inscripciones, incidencias y perfil. --insecure sirve estilos únicamente en la
demostración local con DEBUG=False.

No se requieren modelos nuevos ni migraciones nuevas para la capa HTML.

## Demostración sugerida

1. Inicia sesión como administrador y abre Categorías.
2. Crea una categoría sin dependencias y observa el mensaje de éxito.
3. Abre su detalle, edita el nombre y guarda.
4. Abre Eliminar: el GET solo presenta la confirmación. Confirma y verifica el mensaje.
5. Cambia a voluntario y comprueba que no puede crear actividades ni ver otros perfiles.
6. Crea una inscripción, intenta duplicarla y observa el error sin registros extra.
7. Como coordinador, intenta reducir los cupos por debajo de los inscritos o borrar
   una actividad con dependencias: el sistema debe impedirlo.

## Verificación y límites

Se agregó comunidad/test_web.py con 19 pruebas web: CRUD de las diez entidades,
autenticación, CSRF, permisos, filtros por organización, fechas, cupos, duplicados,
rollback de auditoría, borrado protegido, búsqueda, paginación y escape HTML.
Resultado de la suite completa: **60 pruebas descubiertas, 57 aprobadas y 3
omitidas** (las de concurrencia que requieren MySQL/MariaDB). Las 19 pruebas web
pasaron. Se ejecutó en SQLite en un entorno separado del computador del usuario.
Salida conservada: [evaluacion3-sqlite-tests.txt](evidencias/evaluacion3-sqlite-tests.txt).
`check` no reporta problemas y `makemigrations --check --dry-run` no detecta cambios. Las pruebas renderizan los templates y ejecutan peticiones GET/POST con
el cliente de Django; no equivalen a una revisión visual en navegador.

La vista previa del navegador de este entorno había bloqueado el acceso local;
no se afirma una comprobación visual. La ejecución de esta nueva capa con MariaDB
en el computador del usuario sigue pendiente. Las pruebas anteriores en MariaDB
corresponden a la API previa, no certifican los nuevos formularios web.

Ejecutar en el equipo de entrega:

```powershell
.\.venv\Scripts\python.exe manage.py test comunidad.test_web --noinput -v 2
.\.venv\Scripts\python.exe manage.py test --noinput -v 2
```

Para MariaDB, ejecutar antes scripts/permisos_pruebas.sql como administrador,
según la guía de instalación. La base de pruebas es test_voluntariados.

La implementación cubre la lista de requisitos entregada en esta conversación.
No se ha recibido la rúbrica completa de la Evaluación 3 para certificar otros criterios.
