# Cinco preguntas de preparación

Estas preguntas son de práctica; el profesor puede preguntar otras.

1. **¿Cómo se relacionan voluntarios y actividades?**
   `Perfil` amplía la cuenta Django. `Inscripcion` une un voluntario con una actividad
   y almacena estado y fechas. Su restricción única impide repetir la pareja.
   `Asistencia` añade las horas de una inscripción y solo puede existir una por ella.

2. **¿Qué diferencia hay entre el script SQL y las migraciones?**
   El SQL crea la base, el usuario y sus permisos. La migración traduce los modelos
   a tablas, claves y restricciones. `migrate` aplica esas instrucciones; sin él,
   que la base exista no significa que existan las tablas del sistema.

3. **¿Qué hacen Serializer, ModelViewSet y Router?**
   El serializer convierte datos a JSON y valida entradas. ModelViewSet implementa
   lista, detalle, creación, actualización total/parcial y borrado. Router conecta
   esas acciones con URLs. Ejemplo: POST `/api/inscripciones/` crea una inscripción;
   PATCH `/api/inscripciones/ID/` puede cancelarla si las reglas lo permiten.

4. **¿Cómo evitas sobrecupos y cómo mantienes el historial?**
   Cada escritura valida dentro de una transacción. MySQL bloquea las organizaciones
   antes de consultar cupos o reservas para que dos solicitudes no consuman el mismo
   disponible. Se registra autor, momento, operación y valores anteriores/nuevos.
   Si falla la operación, todo se revierte. Las referencias se protegen de borrados
   que romperían el historial; los eventos de auditoría son de solo lectura.

5. **¿Cómo separas credenciales y controlas el acceso?**
   `settings.py` lee SECRET_KEY y conexión desde variables/.env con python-decouple.
   El `.env` público es solo de demostración; claves privadas van en `.env.local`,
   excluido de Git. Django almacena hashes de contraseñas. Los queryset filtran qué
   registros puede ver cada persona y las validaciones autorizan qué puede cambiar:
   voluntario propio, coordinador de organización y administrador global.

## Demostración sugerida

Muestra modelos y relaciones, aplica migraciones, inicia sesión y realiza GET de
lista y detalle, POST, PUT, PATCH y DELETE sobre una categoría sin dependencias.
Después cambia a voluntario para inscribirte, demuestra un duplicado rechazado y
consulta indicadores/auditoría como coordinador. Explica por qué un voluntario no
puede leer auditorías ni cambiar su rol. Conserva las salidas de tests y el commit
exacto que entregas.
