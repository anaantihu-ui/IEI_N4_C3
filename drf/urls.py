"""
URL configuration for drf project.
"""
from django.contrib import admin
from django.urls import path, include
from mi_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.bienvenida, name='bienvenida'),
    path('api/', include('mi_app.urls')),
]

handler404 = 'mi_app.views.mi_error_404'
