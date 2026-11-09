from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers
from . import models as m
from .access import administrador, coordinador, exigir_gestion, perfil, actividades_visibles


def value(serializer, attrs, field, default=None):
    return attrs.get(field, getattr(serializer.instance, field, default))


def fixed(serializer, attrs, fields):
    if serializer.instance:
        for field in fields:
            if field in attrs and attrs[field] != getattr(serializer.instance, field):
                raise serializers.ValidationError({field: 'La relación no puede cambiar; conserva el historial y crea otro registro.'})


def peak_usage(recurso, exclude=None, extra=None):
    events = []
    assignments = recurso.asignaciones.filter(activa=True).exclude(
        actividad__estado__in=['cancelada', 'finalizada']).select_related('actividad')
    if exclude:
        assignments = assignments.exclude(pk=exclude)
    for a in assignments:
        events.extend([(a.actividad.inicio, a.cantidad), (a.actividad.fin, -a.cantidad)])
    if extra:
        start, end, quantity = extra
        events.extend([(start, quantity), (end, -quantity)])
    current = peak = 0
    for _, delta in sorted(events):
        current += delta
        peak = max(peak, current)
    return peak


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        read_only_fields = ['creado_en', 'actualizado_en']


class OrganizacionSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = m.Organizacion


class CategoriaSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = m.Categoria


class PerfilSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username', max_length=150, validators=[UnicodeUsernameValidator()])
    email = serializers.EmailField(source='usuario.email', required=False, allow_blank=True)
    first_name = serializers.CharField(source='usuario.first_name', required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(source='usuario.last_name', required=False, allow_blank=True, max_length=150)
    password = serializers.CharField(write_only=True, required=False, trim_whitespace=False)

    class Meta:
        model = m.Perfil
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'rol', 'organizacion', 'telefono', 'habilidades', 'creado_en', 'actualizado_en']
        read_only_fields = ['creado_en', 'actualizado_en']

    def validate(self, attrs):
        user = self.context['request'].user
        if not administrador(user):
            if not self.instance or self.instance.usuario_id != user.pk:
                raise serializers.ValidationError('Solo puedes editar tu propio perfil.')
            fixed(self, attrs, ['rol', 'organizacion'])
        if not self.instance and 'password' not in attrs:
            raise serializers.ValidationError({'password': 'Es obligatoria para crear la cuenta.'})
        if 'password' in attrs:
            try:
                validate_password(attrs['password'], self.instance.usuario if self.instance else None)
            except DjangoValidationError as exc:
                raise serializers.ValidationError({'password': exc.messages})
        account = attrs.get('usuario', {})
        if 'username' in account:
            qs = get_user_model().objects.filter(username=account['username'])
            if self.instance:
                qs = qs.exclude(pk=self.instance.usuario_id)
            if qs.exists():
                raise serializers.ValidationError({'username': 'Ya existe esta cuenta.'})
        if value(self, attrs, 'rol', 'voluntario') == 'coordinador' and not value(self, attrs, 'organizacion'):
            raise serializers.ValidationError({'organizacion': 'Un coordinador debe pertenecer a una organización.'})
        if self.instance and (self.instance.actividades_coordinadas.exists() or self.instance.inscripciones.exists()):
            fixed(self, attrs, ['rol', 'organizacion'])
        return attrs

    def create(self, validated_data):
        account = validated_data.pop('usuario')
        password = validated_data.pop('password')
        user = get_user_model().objects.create_user(password=password, **account)
        return m.Perfil.objects.create(usuario=user, **validated_data)

    def update(self, instance, validated_data):
        for field, val in validated_data.pop('usuario', {}).items():
            setattr(instance.usuario, field, val)
        if 'password' in validated_data:
            instance.usuario.set_password(validated_data.pop('password'))
        instance.usuario.save()
        return super().update(instance, validated_data)


class OrganizacionScopedSerializer(BaseSerializer):
    def validate(self, attrs):
        fixed(self, attrs, ['organizacion'])
        org = value(self, attrs, 'organizacion')
        exigir_gestion(self.context['request'].user, org)
        if not org.activa:
            raise serializers.ValidationError('La organización está inactiva.')
        return attrs


class UbicacionSerializer(OrganizacionScopedSerializer):
    class Meta(BaseSerializer.Meta):
        model = m.Ubicacion


class ActividadSerializer(OrganizacionScopedSerializer):
    cupos_disponibles = serializers.SerializerMethodField()
    lugar = serializers.CharField(source='ubicacion.direccion', read_only=True)
    comuna = serializers.CharField(source='ubicacion.comuna', read_only=True)

    class Meta(BaseSerializer.Meta):
        model = m.Actividad

    def get_cupos_disponibles(self, obj):
        return max(0, obj.cupos - obj.inscripciones.filter(estado='confirmada').count())

    def validate(self, attrs):
        super().validate(attrs)
        org = value(self, attrs, 'organizacion')
        coord, place = value(self, attrs, 'coordinador'), value(self, attrs, 'ubicacion')
        if coord.rol != 'coordinador' or coord.organizacion_id != org.pk or not coord.usuario.is_active:
            raise serializers.ValidationError({'coordinador': 'Debe ser un coordinador activo de la misma organización.'})
        if place.organizacion_id != org.pk:
            raise serializers.ValidationError({'ubicacion': 'Debe pertenecer a la misma organización.'})
        start, end = value(self, attrs, 'inicio'), value(self, attrs, 'fin')
        if end <= start:
            raise serializers.ValidationError({'fin': 'Debe ser posterior al inicio.'})
        state = value(self, attrs, 'estado', 'borrador')
        if not self.instance and state not in ['borrador', 'publicada']:
            raise serializers.ValidationError({'estado': 'Una actividad nueva comienza como borrador o publicada.'})
        if not self.instance and start <= timezone.now():
            raise serializers.ValidationError({'inicio': 'Una nueva actividad debe comenzar en el futuro.'})
        if self.instance:
            transitions = {'borrador': ['publicada', 'cancelada'], 'publicada': ['en_curso', 'cancelada'], 'en_curso': ['finalizada', 'cancelada'], 'finalizada': [], 'cancelada': []}
            old = self.instance.estado
            if state != old and state not in transitions[old]:
                raise serializers.ValidationError({'estado': 'Transición de estado no permitida.'})
            if old in ['cancelada', 'finalizada']:
                for key in ['inicio', 'fin', 'cupos', 'coordinador', 'ubicacion', 'publica']:
                    fixed(self, attrs, [key])
            if self.instance.inscripciones.exists() or self.instance.asignaciones.exists():
                fixed(self, attrs, ['inicio', 'fin'])
            if value(self, attrs, 'cupos') < self.instance.inscripciones.filter(estado='confirmada').count():
                raise serializers.ValidationError({'cupos': 'No puede ser menor al número de inscritos confirmados.'})
        if state == 'en_curso' and start > timezone.now():
            raise serializers.ValidationError({'estado': 'La actividad aún no comienza.'})
        if state == 'finalizada' and end > timezone.now():
            raise serializers.ValidationError({'estado': 'La actividad aún no termina.'})
        return attrs


class InscripcionSerializer(BaseSerializer):
    voluntario = serializers.PrimaryKeyRelatedField(queryset=m.Perfil.objects.all(), required=False)

    class Meta(BaseSerializer.Meta):
        model = m.Inscripcion
        validators = []  # Se verifica con el voluntario inferido dentro de la transacción.

    def validate(self, attrs):
        fixed(self, attrs, ['actividad', 'voluntario'])
        user = self.context['request'].user
        activity = value(self, attrs, 'actividad')
        volunteer = value(self, attrs, 'voluntario', perfil(user))
        if not volunteer or volunteer.rol != 'voluntario' or not volunteer.usuario.is_active:
            raise serializers.ValidationError({'voluntario': 'Se requiere un voluntario activo.'})
        if not administrador(user) and not coordinador(user):
            if volunteer.usuario_id != user.pk:
                raise serializers.ValidationError('No puedes inscribir a otra persona.')
            if not actividades_visibles(user).filter(pk=activity.pk).exists():
                raise serializers.ValidationError('La actividad no está disponible para tu perfil.')
        else:
            exigir_gestion(user, activity.organizacion)
        if not activity.publica and volunteer.organizacion_id != activity.organizacion_id:
            raise serializers.ValidationError('La actividad privada requiere pertenecer a la organización.')
        if not activity.organizacion.activa:
            raise serializers.ValidationError('La organización está inactiva.')
        attrs['voluntario'] = volunteer
        duplicate = m.Inscripcion.objects.filter(actividad=activity, voluntario=volunteer)
        if self.instance:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise serializers.ValidationError('Este voluntario ya tiene una inscripción; modifica su estado.')
        state = value(self, attrs, 'estado', 'confirmada')
        if not self.instance and state != 'confirmada':
            raise serializers.ValidationError({'estado': 'Una inscripción nueva comienza confirmada.'})
        changed = not self.instance or state != self.instance.estado
        if changed:
            if activity.estado != 'publicada' or activity.inicio <= timezone.now():
                raise serializers.ValidationError('Las inscripciones solo cambian antes del inicio de una actividad publicada.')
            if state == 'confirmada':
                count = activity.inscripciones.filter(estado='confirmada')
                if self.instance:
                    count = count.exclude(pk=self.instance.pk)
                if count.count() >= activity.cupos:
                    raise serializers.ValidationError('No quedan cupos disponibles.')
            if self.instance and hasattr(self.instance, 'asistencia'):
                raise serializers.ValidationError('No puedes cambiar una inscripción con asistencia registrada.')
        return attrs


class AsistenciaSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = m.Asistencia

    def validate(self, attrs):
        fixed(self, attrs, ['inscripcion'])
        signup = value(self, attrs, 'inscripcion')
        activity = signup.actividad
        exigir_gestion(self.context['request'].user, activity.organizacion)
        if signup.estado != 'confirmada' or activity.estado not in ['en_curso', 'finalizada']:
            raise serializers.ValidationError('Se requiere una inscripción confirmada en una actividad en curso o finalizada.')
        elapsed = Decimal(str(max(0, (min(timezone.now(), activity.fin) - activity.inicio).total_seconds()))) / Decimal('3600')
        if value(self, attrs, 'horas') > elapsed:
            raise serializers.ValidationError({'horas': 'No puede exceder la duración transcurrida de la actividad.'})
        return attrs


class RecursoSerializer(OrganizacionScopedSerializer):
    class Meta(BaseSerializer.Meta):
        model = m.Recurso

    def validate(self, attrs):
        super().validate(attrs)
        if self.instance and value(self, attrs, 'cantidad_total') < peak_usage(self.instance):
            raise serializers.ValidationError({'cantidad_total': 'Hay reservas simultáneas que superan esta cantidad.'})
        return attrs


class AsignacionRecursoSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = m.AsignacionRecurso

    def validate(self, attrs):
        fixed(self, attrs, ['actividad', 'recurso'])
        activity, resource = value(self, attrs, 'actividad'), value(self, attrs, 'recurso')
        exigir_gestion(self.context['request'].user, activity.organizacion)
        if activity.organizacion_id != resource.organizacion_id:
            raise serializers.ValidationError('El recurso y la actividad deben pertenecer a la misma organización.')
        if value(self, attrs, 'activa', True):
            if activity.estado in ['cancelada', 'finalizada']:
                raise serializers.ValidationError('No se reservan recursos para actividades terminadas o canceladas.')
            quantity = value(self, attrs, 'cantidad')
            peak = peak_usage(resource, self.instance.pk if self.instance else None, (activity.inicio, activity.fin, quantity))
            if peak > resource.cantidad_total:
                raise serializers.ValidationError({'cantidad': 'No hay recursos suficientes en ese intervalo.'})
        return attrs


class IncidenciaSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = m.Incidencia
        read_only_fields = BaseSerializer.Meta.read_only_fields + ['reportante']

    def validate(self, attrs):
        fixed(self, attrs, ['actividad'])
        user = self.context['request'].user
        activity = value(self, attrs, 'actividad')
        if administrador(user) or coordinador(user):
            exigir_gestion(user, activity.organizacion)
        else:
            if not activity.inscripciones.filter(voluntario__usuario=user).exists():
                raise serializers.ValidationError('Solo puedes reportar incidencias de actividades en las que participas.')
            if self.instance:
                if self.instance.estado != 'abierta':
                    raise serializers.ValidationError('Una incidencia en revisión no puede editarse por el reportante.')
                fixed(self, attrs, ['estado', 'resolucion'])
            elif attrs.get('estado', 'abierta') != 'abierta' or attrs.get('resolucion'):
                raise serializers.ValidationError('Solo un coordinador puede gestionar la resolución.')
        state = value(self, attrs, 'estado', 'abierta')
        if self.instance and state != self.instance.estado:
            transitions = {'abierta': ['en_revision', 'resuelta'], 'en_revision': ['resuelta'], 'resuelta': []}
            if state not in transitions[self.instance.estado]:
                raise serializers.ValidationError({'estado': 'Transición no permitida.'})
        if state == 'resuelta' and not value(self, attrs, 'resolucion', '').strip():
            raise serializers.ValidationError({'resolucion': 'Debes explicar cómo se resolvió la incidencia.'})
        return attrs


class EventoAuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.EventoAuditoria
        fields = '__all__'
        read_only_fields = [f.name for f in m.EventoAuditoria._meta.fields]
