from django.shortcuts import render
from rest_framework import viewsets
from .models import (
    Region, Comuna, Perfil, Organizacion, Categoria,
    Estado, Voluntario, Coordinador, Actividad,
    Inscripcion, Recurso, AsignacionRecurso, HistorialEstado
)
from .serializer import (
    RegionSerializer, ComunaSerializer, PerfilSerializer,
    OrganizacionSerializer, CategoriaSerializer, EstadoSerializer,
    VoluntarioSerializer, CoordinadorSerializer, ActividadSerializer,
    InscripcionSerializer, RecursoSerializer, AsignacionRecursoSerializer,
    HistorialEstadoSerializer
)


def bienvenida(request):
    return render(request, 'bienvenida.html')


def mi_error_404(request, exception):
    return render(request, '404.html', status=404)


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class ComunaViewSet(viewsets.ModelViewSet):
    queryset = Comuna.objects.all()
    serializer_class = ComunaSerializer


class PerfilViewSet(viewsets.ModelViewSet):
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer


class OrganizacionViewSet(viewsets.ModelViewSet):
    queryset = Organizacion.objects.all()
    serializer_class = OrganizacionSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer


class VoluntarioViewSet(viewsets.ModelViewSet):
    queryset = Voluntario.objects.all()
    serializer_class = VoluntarioSerializer


class CoordinadorViewSet(viewsets.ModelViewSet):
    queryset = Coordinador.objects.all()
    serializer_class = CoordinadorSerializer


class ActividadViewSet(viewsets.ModelViewSet):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer


class InscripcionViewSet(viewsets.ModelViewSet):
    queryset = Inscripcion.objects.all()
    serializer_class = InscripcionSerializer


class RecursoViewSet(viewsets.ModelViewSet):
    queryset = Recurso.objects.all()
    serializer_class = RecursoSerializer


class AsignacionRecursoViewSet(viewsets.ModelViewSet):
    queryset = AsignacionRecurso.objects.all()
    serializer_class = AsignacionRecursoSerializer


class HistorialEstadoViewSet(viewsets.ModelViewSet):
    queryset = HistorialEstado.objects.all()
    serializer_class = HistorialEstadoSerializer
