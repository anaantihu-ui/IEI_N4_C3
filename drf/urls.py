"""Rutas del proyecto Django IEI_N4_C3."""
from django.contrib import admin
from django.urls import path, include
from mi_app import views

urlpatterns = [
    path("api/", include("biblio_app.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path('admin/', admin.site.urls),
    path('', views.bienvenida, name='bienvenida'),
]

# Se conserva el manejador 404 original.
handler404 = 'mi_app.views.mi_error_404'
