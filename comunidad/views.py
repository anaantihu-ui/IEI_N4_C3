import json
from datetime import timedelta, timezone as datetime_timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError, transaction
from django.db.models import Count, Sum
from django.db.models.deletion import ProtectedError
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from . import models as m, serializers as s
from .access import administrador, coordinador, exigir_gestion, perfil, actividades_visibles


class Acceso(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS and getattr(view, 'lectura_publica', False):
            return True
        return request.user.is_authenticated


def organization_id(obj):
    if isinstance(obj, m.Organizacion):
        return obj.pk
    if hasattr(obj, 'organizacion_id'):
        return obj.organizacion_id
    if hasattr(obj, 'actividad'):
        return obj.actividad.organizacion_id
    if hasattr(obj, 'inscripcion'):
        return obj.inscripcion.actividad.organizacion_id
    return None


def audit(obj, actor, action, before, after):
    # Serializadores excluyen contraseñas de sus respuestas y del historial.
    m.EventoAuditoria.objects.create(
        organizacion_id=organization_id(obj), entidad=obj._meta.model_name,
        objeto_id=obj.pk, accion=action, actor=actor, actor_nombre=actor.username,
        estado_anterior=before.get('estado', ''), estado_nuevo=after.get('estado', ''),
        anterior=json.loads(json.dumps(before, cls=DjangoJSONEncoder)),
        posterior=json.loads(json.dumps(after, cls=DjangoJSONEncoder)),
    )


class AuditedViewSet(viewsets.ModelViewSet):
    permission_classes = [Acceso]
    ordering_fields = ['id', 'creado_en', 'actualizado_en']
    ordering = ['id']

    def transactional(self, operation, *args, **kwargs):
        try:
            with transaction.atomic():
                # Orden único de bloqueos para cupos, reservas y cambios relacionados.
                # Adecuado al proyecto académico: serializa escrituras entre organizaciones.
                list(m.Organizacion.objects.select_for_update().order_by('pk').values_list('pk', flat=True))
                return operation(*args, **kwargs)
        except ProtectedError:
            return Response({'detail': 'Hay registros relacionados. Conserva el historial y cambia el estado en lugar de eliminar.'}, status=409)
        except IntegrityError:
            return Response({'detail': 'La operación viola una restricción de integridad o unicidad.'}, status=400)

    def create(self, request, *args, **kwargs):
        return self.transactional(super().create, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return self.transactional(super().update, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return self.transactional(super().destroy, request, *args, **kwargs)

    def perform_create(self, serializer):
        obj = serializer.save(**self.creation_kwargs())
        audit(obj, self.request.user, 'crear', {}, self.get_serializer(obj).data)

    def creation_kwargs(self):
        return {}

    def perform_update(self, serializer):
        before = self.get_serializer(serializer.instance).data
        obj = serializer.save()
        audit(obj, self.request.user, 'modificar', before, self.get_serializer(obj).data)
        self.after_update(obj, before)

    def after_update(self, obj, before):
        pass

    def perform_destroy(self, instance):
        self.check_deletion(instance)
        audit(instance, self.request.user, 'eliminar', self.get_serializer(instance).data, {})
        instance.delete()

    def check_deletion(self, obj):
        if not administrador(self.request.user):
            org_id = organization_id(obj)
            if not org_id:
                raise PermissionDenied('Esta operación requiere administrador.')
            exigir_gestion(self.request.user, m.Organizacion.objects.get(pk=org_id))


class AdminWriteViewSet(AuditedViewSet):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if request.method not in permissions.SAFE_METHODS and not administrador(request.user):
            raise PermissionDenied('Solo el administrador puede modificar este catálogo.')


class OrganizacionViewSet(AdminWriteViewSet):
    serializer_class = s.OrganizacionSerializer
    lectura_publica = True
    search_fields = ['nombre', 'descripcion']

    def get_queryset(self):
        qs = m.Organizacion.objects.all()
        return qs if administrador(self.request.user) else qs.filter(activa=True)


class CategoriaViewSet(AdminWriteViewSet):
    queryset = m.Categoria.objects.all()
    serializer_class = s.CategoriaSerializer
    lectura_publica = True
    search_fields = ['nombre', 'descripcion']


class PerfilViewSet(AuditedViewSet):
    serializer_class = s.PerfilSerializer
    search_fields = ['usuario__username', 'habilidades']

    def get_queryset(self):
        qs = m.Perfil.objects.select_related('usuario', 'organizacion')
        return qs if administrador(self.request.user) else qs.filter(usuario=self.request.user)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if request.method in ['POST', 'DELETE'] and not administrador(request.user):
            raise PermissionDenied('La creación y eliminación de cuentas requiere administrador.')

    def perform_destroy(self, instance):
        user = instance.usuario
        super().perform_destroy(instance)
        user.delete()


class OrganizationViewSet(AuditedViewSet):
    def get_queryset(self):
        qs = super().get_queryset()
        if administrador(self.request.user):
            return qs
        if coordinador(self.request.user):
            return qs.filter(organizacion=perfil(self.request.user).organizacion)
        return qs.none()


class UbicacionViewSet(OrganizationViewSet):
    queryset = m.Ubicacion.objects.select_related('organizacion')
    serializer_class = s.UbicacionSerializer
    search_fields = ['nombre', 'comuna', 'direccion']


class ActividadViewSet(AuditedViewSet):
    serializer_class = s.ActividadSerializer
    lectura_publica = True
    search_fields = ['titulo', 'descripcion', 'ubicacion__comuna', 'categoria__nombre']
    ordering_fields = ['id', 'inicio', 'fin', 'titulo', 'creado_en']

    def get_queryset(self):
        qs = actividades_visibles(self.request.user)
        for field in ['organizacion', 'categoria', 'estado']:
            val = self.request.query_params.get(field)
            if val:
                if field != 'estado' and not val.isdigit():
                    raise ValidationError({field: 'Debe ser un identificador numérico.'})
                qs = qs.filter(**{field: val})
        for name, lookup in [('desde', 'inicio__gte'), ('hasta', 'inicio__lte')]:
            raw = self.request.query_params.get(name)
            if raw:
                try:
                    dt = parse_datetime(raw)
                except ValueError:
                    dt = None
                if not dt:
                    raise ValidationError({name: 'Usa fecha ISO 8601, por ejemplo 2026-12-01T00:00:00Z.'})
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt)
                qs = qs.filter(**{lookup: dt})
        return qs

    def check_deletion(self, obj):
        super().check_deletion(obj)
        if obj.inicio <= timezone.now() or obj.estado in ['en_curso', 'finalizada', 'cancelada']:
            raise ValidationError('Conserva la actividad histórica; no puede eliminarse.')

    def after_update(self, obj, before):
        if before['estado'] == obj.estado or obj.estado not in ['cancelada', 'finalizada']:
            return
        if obj.estado == 'cancelada':
            for signup in obj.inscripciones.filter(estado='confirmada'):
                old = s.InscripcionSerializer(signup).data
                signup.estado = 'cancelada'
                signup.save()
                audit(signup, self.request.user, 'modificar', old, s.InscripcionSerializer(signup).data)
        for allocation in obj.asignaciones.filter(activa=True):
            old = s.AsignacionRecursoSerializer(allocation).data
            allocation.activa = False
            allocation.save()
            audit(allocation, self.request.user, 'modificar', old, s.AsignacionRecursoSerializer(allocation).data)

    @action(detail=False, methods=['get'])
    def indicadores(self, request):
        if not (administrador(request.user) or coordinador(request.user)):
            raise PermissionDenied('Los indicadores privados requieren coordinador o administrador.')
        activities = self.filter_queryset(self.get_queryset())
        if not administrador(request.user):
            activities = activities.filter(organizacion=perfil(request.user).organizacion)
        signups = m.Inscripcion.objects.filter(actividad__in=activities)
        attendance = m.Asistencia.objects.filter(inscripcion__in=signups)
        allocated = m.AsignacionRecurso.objects.filter(actividad__in=activities, activa=True).exclude(actividad__estado__in=['finalizada', 'cancelada'])
        now = timezone.now()
        resources = m.Recurso.objects.all()
        if not administrador(request.user):
            resources = resources.filter(organizacion=perfil(request.user).organizacion)
        resources = resources.filter(organizacion_id__in=activities.values('organizacion_id'))
        active_units = allocated.filter(actividad__inicio__lte=now, actividad__fin__gt=now).aggregate(n=Sum('cantidad'))['n'] or 0
        units = resources.aggregate(n=Sum('cantidad_total'))['n'] or 0
        capacity = activities.exclude(estado__in=['cancelada', 'borrador']).aggregate(n=Sum('cupos'))['n'] or 0
        confirmed = signups.filter(estado='confirmada').count()
        return Response({
            'actividades': activities.count(),
            'actividades_por_estado': list(activities.order_by().values('estado').annotate(total=Count('id'))),
            'inscripciones': signups.count(), 'inscripciones_confirmadas': confirmed,
            'inscripciones_ultimos_30_dias': signups.filter(creado_en__gte=now - timedelta(days=30)).count(),
            'voluntarios_distintos': signups.values('voluntario_id').distinct().count(),
            'asistencias': attendance.count(),
            'horas_voluntariado': attendance.aggregate(n=Sum('horas'))['n'] or 0,
            'ocupacion_porcentaje': round(100 * confirmed / capacity, 2) if capacity else 0,
            'recursos_unidades_en_uso_ahora': active_units,
            'recursos_unidades_totales': units,
            'utilizacion_actual_porcentaje': round(100 * active_units / units, 2) if units else 0,
            'incidencias_pendientes': m.Incidencia.objects.filter(actividad__in=activities).exclude(estado='resuelta').count(),
            'zona_horaria_tendencia': 'UTC',
            'inscripciones_por_mes': list(signups.annotate(mes=TruncMonth('creado_en', tzinfo=datetime_timezone.utc)).values('mes').annotate(total=Count('id')).order_by('mes')),
        })


class InscripcionViewSet(AuditedViewSet):
    serializer_class = s.InscripcionSerializer

    def get_queryset(self):
        qs = m.Inscripcion.objects.select_related('actividad__organizacion', 'voluntario__usuario')
        if administrador(self.request.user):
            return qs
        if coordinador(self.request.user):
            return qs.filter(actividad__organizacion=perfil(self.request.user).organizacion)
        return qs.filter(voluntario__usuario=self.request.user)

    def check_deletion(self, obj):
        if not administrador(self.request.user) and not coordinador(self.request.user):
            if obj.voluntario.usuario_id != self.request.user.pk:
                raise PermissionDenied()
        else:
            super().check_deletion(obj)
        if obj.actividad.inicio <= timezone.now() or obj.actividad.estado != 'publicada':
            raise ValidationError('Conserva la inscripción histórica; no puede eliminarse.')


class AsistenciaViewSet(AuditedViewSet):
    serializer_class = s.AsistenciaSerializer

    def get_queryset(self):
        qs = m.Asistencia.objects.select_related('inscripcion__actividad__organizacion')
        if administrador(self.request.user):
            return qs
        if coordinador(self.request.user):
            return qs.filter(inscripcion__actividad__organizacion=perfil(self.request.user).organizacion)
        return qs.filter(inscripcion__voluntario__usuario=self.request.user)


class RecursoViewSet(OrganizationViewSet):
    queryset = m.Recurso.objects.select_related('organizacion')
    serializer_class = s.RecursoSerializer
    search_fields = ['nombre', 'descripcion']


class AsignacionRecursoViewSet(AuditedViewSet):
    serializer_class = s.AsignacionRecursoSerializer

    def get_queryset(self):
        qs = m.AsignacionRecurso.objects.select_related('actividad__organizacion', 'recurso')
        if administrador(self.request.user):
            return qs
        if coordinador(self.request.user):
            return qs.filter(actividad__organizacion=perfil(self.request.user).organizacion)
        return qs.none()


class IncidenciaViewSet(AuditedViewSet):
    serializer_class = s.IncidenciaSerializer

    def get_queryset(self):
        qs = m.Incidencia.objects.select_related('actividad__organizacion', 'reportante')
        if administrador(self.request.user):
            return qs
        if coordinador(self.request.user):
            return qs.filter(actividad__organizacion=perfil(self.request.user).organizacion)
        return qs.filter(reportante=self.request.user)

    def creation_kwargs(self):
        return {'reportante': self.request.user}

    def check_deletion(self, obj):
        if obj.estado != 'abierta':
            raise ValidationError('Conserva las incidencias revisadas como antecedentes históricos.')
        if obj.reportante_id != self.request.user.pk:
            super().check_deletion(obj)


class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = s.EventoAuditoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = m.EventoAuditoria.objects.all()
        if not administrador(self.request.user):
            if not coordinador(self.request.user):
                raise PermissionDenied('La auditoría requiere coordinador o administrador.')
            qs = qs.filter(organizacion_id=perfil(self.request.user).organizacion_id).exclude(entidad='perfil')
        for field in ['entidad', 'accion', 'objeto_id']:
            val = self.request.query_params.get(field)
            if val:
                if field == 'objeto_id' and not val.isdigit():
                    raise ValidationError({'objeto_id': 'Debe ser numérico.'})
                qs = qs.filter(**{field: val})
        return qs
