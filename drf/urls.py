from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("web/", include("comunidad.web_urls")),
    path("", RedirectView.as_view(url="/web/actividades/", permanent=False)),
    path("api/", include("comunidad.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("admin/", admin.site.urls),
]
