from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("paises", views.PaisViewSet, basename="paises")
router.register("regiones", views.RegionViewSet, basename="regiones")
router.register("provincias", views.ProvinciaViewSet, basename="provincias")
router.register("comunas", views.ComunaViewSet, basename="comunas")
router.register("direcciones", views.DireccionViewSet, basename="direcciones")
router.register("bibliotecas", views.BibliotecaViewSet, basename="bibliotecas")
router.register("autores", views.AutorViewSet, basename="autores")
router.register("generos", views.GeneroViewSet, basename="generos")
router.register("subgeneros", views.SubGeneroViewSet, basename="subgeneros")
router.register("editoriales", views.EditorialViewSet, basename="editoriales")
router.register("idiomas", views.IdiomaViewSet, basename="idiomas")
router.register("ediciones", views.EdicionViewSet, basename="ediciones")
router.register("libros", views.LibroViewSet, basename="libros")
router.register("estados", views.EstadoViewSet, basename="estados")
router.register("ubicaciones", views.UbicacionViewSet, basename="ubicaciones")
router.register("inventarios", views.InventarioViewSet, basename="inventarios")
router.register("usuarios", views.UsuarioViewSet, basename="usuarios")
router.register("prestamos", views.PrestamoViewSet, basename="prestamos")

urlpatterns = router.urls
