# Verificación de Evaluación 2

## Implementación
- Modelo de 18 entidades adaptado del ejemplo docente baileytorch/IEI_N4_C1, commit e030c19cc67fb7a97a0c0b24371235f3868dc277.
- Nueva app biblio_app con migración inicial, 18 ModelSerializer, 18 ModelViewSet y DefaultRouter bajo /api/.
- Django REST Framework declarado en requirements.txt y settings.py.
- Autenticación por cuenta Django; contraseña del lector con hash y write_only.
- Se mantienen las páginas y apps previas, base incidencias, SQL y configuración por entorno.
- README y guía de defensa actualizados para describir la implementación real.

## Validación
- 24 pruebas automatizadas: 18 ciclos CRUD completos con comprobación de persistencia, 4 pruebas de acceso/validación/contraseñas y 2 pruebas de páginas.
- Migración inicial generada desde los modelos de esta app nueva.
- Las comprobaciones de ejecución usan Django y DRF reales sobre SQLite, sin adaptadores simulados.
- SQLite emite 18 avisos W046 por comentarios de tablas del modelo docente; no soporta esos comentarios.

## Pendientes que dependen del equipo de entrega
- Instalar mysqlclient y sus requisitos de compilación si son necesarios.
- Ejecutar el SQL con credenciales locales, comprobar versión MySQL/MariaDB y aplicar migraciones reales.
- Repetir el CRUD con DB_ENGINE=mysql y conservar evidencia de persistencia.
- Practicar las cinco preguntas de la defensa individual.

No se ha certificado una conexión MySQL desde este entorno. El verificador estático no sustituye esa prueba. La implementación es CRUD académico; no incluye reglas de stock, multas o reservas.
