"""Adaptador compartido: los formularios conservan permisos, reglas y auditoría REST.

No hace solicitudes HTTP internas. Reutiliza los serializers y los métodos de
persistencia de los ViewSets dentro del mismo bloqueo que utiliza la API.
"""
from types import SimpleNamespace
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404
from . import forms as f, views as api, models as m
from .access import administrador, coordinador

# slug: título, formulario, ViewSet
ENTIDADES = {
    'organizaciones': ('Organizaciones', f.OrganizacionForm, api.OrganizacionViewSet),
    'perfiles': ('Personas y perfiles', f.PerfilForm, api.PerfilViewSet),
    'categorias': ('Categorías', f.CategoriaForm, api.CategoriaViewSet),
    'ubicaciones': ('Ubicaciones', f.UbicacionForm, api.UbicacionViewSet),
    'actividades': ('Actividades', f.ActividadForm, api.ActividadViewSet),
    'inscripciones': ('Inscripciones', f.InscripcionForm, api.InscripcionViewSet),
    'asistencias': ('Asistencias', f.AsistenciaForm, api.AsistenciaViewSet),
    'recursos': ('Recursos', f.RecursoForm, api.RecursoViewSet),
    'asignaciones': ('Asignación de recursos', f.AsignacionRecursoForm, api.AsignacionRecursoViewSet),
    'incidencias': ('Incidencias', f.IncidenciaForm, api.IncidenciaViewSet),
}


def viewset(entidad, request):
    view = ENTIDADES[entidad][2]()
    view.request = SimpleNamespace(user=request.user, query_params={})
    view.format_kwarg = None
    view.args, view.kwargs = (), {}
    return view


def puede_escribir(entidad, user, accion, obj=None):
    if administrador(user):
        return True
    if entidad in ['organizaciones', 'categorias']:
        return False
    if entidad == 'perfiles':
        return accion == 'editar' and (obj is None or obj.usuario_id == user.pk)
    if entidad in ['inscripciones', 'incidencias']:
        return bool(coordinador(user) or getattr(user, 'perfil', None))
    if not coordinador(user):
        return False
    return obj is None or api.organization_id(obj) == user.perfil.organizacion_id


def exigir_permiso(entidad, user, accion, obj=None):
    if not puede_escribir(entidad, user, accion, obj):
        raise PermissionDenied('Tu perfil no permite esta operación.')


@transaction.atomic
def guardar(entidad, request, payload, pk=None):
    list(m.Organizacion.objects.select_for_update().order_by('pk').values_list('pk', flat=True))
    view = viewset(entidad, request)
    # Recargar: ModelForm modifica su instancia durante is_valid(). Necesitamos
    # los valores originales para comprobar relaciones inmutables y auditar.
    obj = get_object_or_404(view.get_queryset(), pk=pk) if pk else None
    exigir_permiso(entidad, request.user, 'editar' if pk else 'crear', obj)
    serializer = view.get_serializer(instance=obj, data=payload)
    serializer.is_valid(raise_exception=True)
    if obj:
        view.perform_update(serializer)
    else:
        view.perform_create(serializer)
    return serializer.instance


@transaction.atomic
def eliminar(entidad, request, pk):
    list(m.Organizacion.objects.select_for_update().order_by('pk').values_list('pk', flat=True))
    view = viewset(entidad, request)
    obj = get_object_or_404(view.get_queryset(), pk=pk)
    exigir_permiso(entidad, request.user, 'eliminar', obj)
    view.perform_destroy(obj)
