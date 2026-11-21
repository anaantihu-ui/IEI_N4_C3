# Verificación de esta revisión — 20 de noviembre de 2026

## Código revisado y cambios

Base: commit d3b95b8 de implementacion/voluntariados. Ya existían los modelos,
la migración inicial, diez ModelViewSets operativos, Router, serializers,
roles, auditoría, indicadores, SQL, .env de demostración y 40 pruebas.
No se sustituyó el dominio por un proyecto de biblioteca.

Se detectó una incompatibilidad: requirements.txt usaba Django 5.2.17, que requiere
MariaDB 10.5+, mientras el servidor informado es MariaDB 10.4.32.
Se ajustó a Django 4.2.30 para la entrega local y se cambió condition= por check=
en las restricciones de modelos y migración. No cambia el esquema ni se borra o
reemplaza el historial de migraciones; no se necesita una migración adicional.
Django 4.2 terminó soporte en abril de 2026. Para producción hay que actualizar
MariaDB y Django; esta adaptación responde al servidor académico existente.

También se corrigió la publicación/reprogramación con inicio pasado (prueba de
regresión añadida), se habilitó modo SQL estricto/InnoDB, se bloqueó la selección
accidental de otras bases y se eliminó el restablecimiento automático de claves
al repetir el SQL. Se amplió README y se agregó la guía Windows/phpMyAdmin.

## Ejecutado realmente en el entorno aislado del asistente

Python 3.12.14, Django 4.2.30, DRF 3.16.1, mysqlclient 2.3.2.
Servidor de prueba: **MariaDB 11.8.6**, TCP 127.0.0.1:3307, base voluntariados.
La versión 10.4.32 se comprobó contra la documentación de compatibilidad, pero
NO se ejecutó aquí un servidor de esa versión ni se accedió al XAMPP del usuario.

| Comprobación | Resultado |
|---|---|
| Instalación de requirements y pip check | Correcta, sin dependencias incompatibles |
| SQL principal ejecutado dos veces en MariaDB aislado | Correcto; base y usuarios creados, sin errores al repetir |
| Permisos de aplicación y de pruebas | Limitados a voluntariados y test_voluntariados respectivamente |
| Conexión Django | SELECT DATABASE(), VERSION() confirmó voluntariados y MariaDB 11.8.6 |
| Modo de conexión | STRICT_TRANS_TABLES e InnoDB confirmados por SQL |
| Migraciones SQLite y MariaDB | Aplicadas; migrate --check sin pendientes |
| makemigrations --check --dry-run | No changes detected |
| check --database default | Sin problemas |
| Suite MariaDB | **41 aprobadas, 0 omitidas** |
| Suite SQLite | **38 aprobadas, 3 omitidas** (concurrencia requiere MariaDB/MySQL) |
| HTTP real contra MariaDB aislado | CRUD de categorías: 201/200/204/404; inscripción/cancelación: 201/200; auditoría coordinador 200 y voluntario 403 |
| Carga demo repetida | Ejecutada dos veces; reutiliza cuentas y actividad |
| DB_NAME=incidencias | Configuración rechazada antes de abrir la conexión |
| scripts/verificar_entrega.py | Archivos, .env, SQL y exclusiones coherentes |

Las pruebas CRUD usan el cliente de pruebas de DRF contra la base correspondiente:
GET lista, GET detalle, POST, PUT, PATCH y DELETE en las diez entidades operativas.
Incluyen comprobación de persistencia y 404 posterior al borrado. La auditoría es
intencionalmente de solo lectura. Las pruebas concurrentes disputan el último cupo
y el inventario con reservas simultáneas: comprueban la aceptación/rechazo esperado.

Se verifican permisos entre organizaciones, privacidad de perfiles, hash de claves,
cupos, duplicados, fechas, estados, asistencia, recursos, auditoría e indicadores.
El bloqueo global de organizaciones es una decisión simple para el alcance
académico; serializa escrituras y no está diseñado para gran escala.
Las reglas se aplican en la API; SQL directo/ORM manual puede omitir las validaciones
que no son restricciones de base. El admin del dominio es de solo lectura.

## Evidencias de esta revisión

- [Suite SQLite](evidencias/revision-sqlite.txt).
- [SQL, conexión, migraciones y suite MariaDB](evidencias/revision-mariadb.txt).
- [Carga demo y solicitudes HTTP reales](evidencias/revision-http.txt).
- [Protección de nombre de base](evidencias/revision-proteccion-base.txt).

Los archivos mysql-tests.txt, sqlite-tests.txt y mysql-http.txt sin el prefijo
revision- venían en el repositorio: son evidencias anteriores, no resultados de
esta revisión. No se utilizan para afirmar que se ejecutó algo en el computador
del usuario.

## Pendiente en el computador de entrega

1. Ejecutar crear_base_datos.sql desde phpMyAdmin y comprobar los permisos.
2. Instalar dependencias con Python 3.11/3.12 y configurar .env.local.
3. Verificar la conexión a MariaDB **10.4.32**, ejecutar migrate y la suite allí.
4. Demostrar el CRUD desde Postman o DRF y enviar las capturas indicadas en
   [INSTALACION_WINDOWS.md](INSTALACION_WINDOWS.md).

La base existente incidencias no se ha consultado, borrado ni modificado.
La tabla comunidad_incidencia pertenece exclusivamente a voluntariados.
No se certifica una calificación: esta revisión comprueba el alcance técnico indicado.
