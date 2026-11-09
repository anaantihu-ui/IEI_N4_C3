from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q


class Registro(models.Model):
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['id']


class Organizacion(Registro):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    correo_publico = models.EmailField(blank=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Perfil(Registro):
    class Rol(models.TextChoices):
        VOLUNTARIO = 'voluntario', 'Voluntario'
        COORDINADOR = 'coordinador', 'Coordinador'

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='perfil')
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.VOLUNTARIO)
    organizacion = models.ForeignKey(Organizacion, on_delete=models.PROTECT, null=True, blank=True)
    telefono = models.CharField(max_length=25, blank=True)
    habilidades = models.TextField(blank=True)

    class Meta(Registro.Meta):
        constraints = [models.CheckConstraint(condition=~Q(rol='coordinador') | Q(organizacion__isnull=False), name='coordinador_con_organizacion')]

    def __str__(self):
        return self.usuario.username


class Categoria(Registro):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Ubicacion(Registro):
    organizacion = models.ForeignKey(Organizacion, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=250)
    comuna = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Actividad(Registro):
    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        PUBLICADA = 'publicada', 'Publicada'
        EN_CURSO = 'en_curso', 'En curso'
        FINALIZADA = 'finalizada', 'Finalizada'
        CANCELADA = 'cancelada', 'Cancelada'

    organizacion = models.ForeignKey(Organizacion, on_delete=models.PROTECT)
    coordinador = models.ForeignKey(Perfil, on_delete=models.PROTECT, related_name='actividades_coordinadas')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.PROTECT)
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    cupos = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    publica = models.BooleanField(default=True)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.BORRADOR)

    class Meta(Registro.Meta):
        constraints = [
            models.CheckConstraint(condition=Q(fin__gt=F('inicio')), name='actividad_fechas_validas'),
            models.CheckConstraint(condition=Q(cupos__gte=1), name='actividad_cupos_positivos'),
        ]
        indexes = [models.Index(fields=['organizacion', 'estado', 'inicio'])]

    def __str__(self):
        return self.titulo


class Inscripcion(Registro):
    class Estado(models.TextChoices):
        CONFIRMADA = 'confirmada', 'Confirmada'
        CANCELADA = 'cancelada', 'Cancelada'

    actividad = models.ForeignKey(Actividad, on_delete=models.PROTECT, related_name='inscripciones')
    voluntario = models.ForeignKey(Perfil, on_delete=models.PROTECT, related_name='inscripciones')
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.CONFIRMADA)
    observaciones = models.TextField(blank=True)

    class Meta(Registro.Meta):
        constraints = [models.UniqueConstraint(fields=['actividad', 'voluntario'], name='inscripcion_unica')]


class Asistencia(Registro):
    inscripcion = models.OneToOneField(Inscripcion, on_delete=models.PROTECT, related_name='asistencia')
    horas = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    observaciones = models.TextField(blank=True)

    class Meta(Registro.Meta):
        constraints = [models.CheckConstraint(condition=Q(horas__gte=0), name='asistencia_horas_no_negativas')]


class Recurso(Registro):
    organizacion = models.ForeignKey(Organizacion, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=100)
    cantidad_total = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    descripcion = models.TextField(blank=True)

    class Meta(Registro.Meta):
        constraints = [models.CheckConstraint(condition=Q(cantidad_total__gte=1), name='recurso_cantidad_positiva')]


class AsignacionRecurso(Registro):
    actividad = models.ForeignKey(Actividad, on_delete=models.PROTECT, related_name='asignaciones')
    recurso = models.ForeignKey(Recurso, on_delete=models.PROTECT, related_name='asignaciones')
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    activa = models.BooleanField(default=True)

    class Meta(Registro.Meta):
        constraints = [
            models.UniqueConstraint(fields=['actividad', 'recurso'], name='asignacion_unica'),
            models.CheckConstraint(condition=Q(cantidad__gte=1), name='asignacion_cantidad_positiva'),
        ]


class Incidencia(Registro):
    class Estado(models.TextChoices):
        ABIERTA = 'abierta', 'Abierta'
        EN_REVISION = 'en_revision', 'En revisión'
        RESUELTA = 'resuelta', 'Resuelta'

    actividad = models.ForeignKey(Actividad, on_delete=models.PROTECT, related_name='incidencias')
    reportante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    descripcion = models.TextField()
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.ABIERTA)
    resolucion = models.TextField(blank=True)


class EventoAuditoria(models.Model):
    # IDs y snapshots permiten conservar el registro aunque se elimine la entidad.
    organizacion_id = models.PositiveBigIntegerField(null=True, db_index=True)
    entidad = models.CharField(max_length=80)
    objeto_id = models.PositiveBigIntegerField()
    accion = models.CharField(max_length=12, choices=[('crear', 'Crear'), ('modificar', 'Modificar'), ('eliminar', 'Eliminar')])
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    actor_nombre = models.CharField(max_length=150)
    fecha = models.DateTimeField(auto_now_add=True)
    estado_anterior = models.CharField(max_length=20, blank=True)
    estado_nuevo = models.CharField(max_length=20, blank=True)
    anterior = models.JSONField(default=dict)
    posterior = models.JSONField(default=dict)

    class Meta:
        ordering = ['-fecha', '-id']
        indexes = [models.Index(fields=['entidad', 'objeto_id'])]
