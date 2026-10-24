from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from . import models, serializers

class PaisViewSet(viewsets.ModelViewSet):
    queryset = models.Pais.objects.all().order_by("pk")
    serializer_class = serializers.PaisSerializer
    permission_classes = [IsAuthenticated]


class RegionViewSet(viewsets.ModelViewSet):
    queryset = models.Region.objects.all().order_by("pk")
    serializer_class = serializers.RegionSerializer
    permission_classes = [IsAuthenticated]


class ProvinciaViewSet(viewsets.ModelViewSet):
    queryset = models.Provincia.objects.all().order_by("pk")
    serializer_class = serializers.ProvinciaSerializer
    permission_classes = [IsAuthenticated]


class ComunaViewSet(viewsets.ModelViewSet):
    queryset = models.Comuna.objects.all().order_by("pk")
    serializer_class = serializers.ComunaSerializer
    permission_classes = [IsAuthenticated]


class DireccionViewSet(viewsets.ModelViewSet):
    queryset = models.Direccion.objects.all().order_by("pk")
    serializer_class = serializers.DireccionSerializer
    permission_classes = [IsAuthenticated]


class BibliotecaViewSet(viewsets.ModelViewSet):
    queryset = models.Biblioteca.objects.all().order_by("pk")
    serializer_class = serializers.BibliotecaSerializer
    permission_classes = [IsAuthenticated]


class AutorViewSet(viewsets.ModelViewSet):
    queryset = models.Autor.objects.all().order_by("pk")
    serializer_class = serializers.AutorSerializer
    permission_classes = [IsAuthenticated]


class GeneroViewSet(viewsets.ModelViewSet):
    queryset = models.Genero.objects.all().order_by("pk")
    serializer_class = serializers.GeneroSerializer
    permission_classes = [IsAuthenticated]


class SubGeneroViewSet(viewsets.ModelViewSet):
    queryset = models.SubGenero.objects.all().order_by("pk")
    serializer_class = serializers.SubGeneroSerializer
    permission_classes = [IsAuthenticated]


class EditorialViewSet(viewsets.ModelViewSet):
    queryset = models.Editorial.objects.all().order_by("pk")
    serializer_class = serializers.EditorialSerializer
    permission_classes = [IsAuthenticated]


class IdiomaViewSet(viewsets.ModelViewSet):
    queryset = models.Idioma.objects.all().order_by("pk")
    serializer_class = serializers.IdiomaSerializer
    permission_classes = [IsAuthenticated]


class EdicionViewSet(viewsets.ModelViewSet):
    queryset = models.Edicion.objects.all().order_by("pk")
    serializer_class = serializers.EdicionSerializer
    permission_classes = [IsAuthenticated]


class LibroViewSet(viewsets.ModelViewSet):
    queryset = models.Libro.objects.all().order_by("pk")
    serializer_class = serializers.LibroSerializer
    permission_classes = [IsAuthenticated]


class EstadoViewSet(viewsets.ModelViewSet):
    queryset = models.Estado.objects.all().order_by("pk")
    serializer_class = serializers.EstadoSerializer
    permission_classes = [IsAuthenticated]


class UbicacionViewSet(viewsets.ModelViewSet):
    queryset = models.Ubicacion.objects.all().order_by("pk")
    serializer_class = serializers.UbicacionSerializer
    permission_classes = [IsAuthenticated]


class InventarioViewSet(viewsets.ModelViewSet):
    queryset = models.Inventario.objects.all().order_by("pk")
    serializer_class = serializers.InventarioSerializer
    permission_classes = [IsAuthenticated]


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = models.Usuario.objects.all().order_by("pk")
    serializer_class = serializers.UsuarioSerializer
    permission_classes = [IsAuthenticated]


class PrestamoViewSet(viewsets.ModelViewSet):
    queryset = models.Prestamo.objects.all().order_by("pk")
    serializer_class = serializers.PrestamoSerializer
    permission_classes = [IsAuthenticated]


