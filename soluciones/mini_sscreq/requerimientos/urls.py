from django.urls import path

from . import views

app_name = "requerimientos"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("nuevo/", views.formulario, name="nuevo"),
    path("<int:pk>/editar/", views.formulario, name="editar"),
    path("<int:pk>/estatus/", views.cambiar_estatus, name="cambiar_estatus"),
    path("<int:pk>/borrar/", views.borrar, name="borrar"),
]
