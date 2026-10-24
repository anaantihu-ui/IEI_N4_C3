from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from . import models

class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pais
        fields = "__all__"


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Region
        fields = "__all__"


class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Provincia
        fields = "__all__"


class ComunaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comuna
        fields = "__all__"


class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Direccion
        fields = "__all__"


class BibliotecaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Biblioteca
        fields = "__all__"


class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Autor
        fields = "__all__"


class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genero
        fields = "__all__"


class SubGeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubGenero
        fields = "__all__"


class EditorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Editorial
        fields = "__all__"


class IdiomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Idioma
        fields = "__all__"


class EdicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Edicion
        fields = "__all__"


class LibroSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Libro
        fields = "__all__"

    def validate_paginas(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad de páginas debe ser positiva.")
        return value


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Estado
        fields = "__all__"


class UbicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ubicacion
        fields = "__all__"


class InventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Inventario
        fields = "__all__"


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Usuario
        fields = "__all__"
        extra_kwargs = {"contrasenia": {"write_only": True, "required": False, "allow_null": False, "allow_blank": False}}

    def validate_contrasenia(self, value):
        return make_password(value)


class PrestamoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Prestamo
        fields = "__all__"

    def validate(self, attrs):
        from django.utils import timezone
        inicio = self.instance.fecha_prestamo if self.instance else timezone.now()
        devolucion = attrs.get("fecha_devolucion", getattr(self.instance, "fecha_devolucion", None))
        retorno = attrs.get("fecha_retorno", getattr(self.instance, "fecha_retorno", None))
        if devolucion and devolucion < inicio:
            raise serializers.ValidationError({"fecha_devolucion": "Debe ser posterior al préstamo."})
        if retorno and retorno < inicio:
            raise serializers.ValidationError({"fecha_retorno": "No puede ser anterior al préstamo."})
        return attrs


