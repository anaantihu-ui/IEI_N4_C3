"""
URL configuration for drf project.
"""
from django.contrib import admin
from django.urls import path
from mi_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.bienvenida, name='bienvenida'),
]

# Manejador personalizado para el error 404
handler404 = 'mi_app.views.mi_error_404'