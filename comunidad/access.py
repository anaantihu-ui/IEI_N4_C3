from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from .models import Actividad, Perfil


def perfil(user):
    return getattr(user, 'perfil', None) if user.is_authenticated else None


def administrador(user):
    return bool(user.is_authenticated and user.is_superuser)


def coordinador(user):
    p = perfil(user)
    return bool(p and p.rol == Perfil.Rol.COORDINADOR and p.organizacion.activa)


def exigir_gestion(user, organizacion):
    if administrador(user):
        return
    p = perfil(user)
    if not coordinador(user) or p.organizacion_id != organizacion.pk:
        raise PermissionDenied('Solo el coordinador de esta organización puede realizar esta operación.')


def actividades_visibles(user):
    qs = Actividad.objects.select_related('organizacion', 'ubicacion', 'categoria', 'coordinador')
    if administrador(user):
        return qs
    publicas = Q(publica=True) & ~Q(estado=Actividad.Estado.BORRADOR) & Q(organizacion__activa=True)
    p = perfil(user)
    if coordinador(user):
        return qs.filter(publicas | Q(organizacion_id=p.organizacion_id))
    if p:
        internas = Q(organizacion_id=p.organizacion_id, organizacion__activa=True) & ~Q(estado=Actividad.Estado.BORRADOR) if p.organizacion_id else Q(pk__in=[])
        # Se mantiene acceso a actividades históricas en las que participó.
        return qs.filter(publicas | internas | Q(inscripciones__voluntario=p)).distinct()
    return qs.filter(publicas)
