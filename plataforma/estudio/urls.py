from django.urls import path

from . import views

app_name = "estudio"

urlpatterns = [
    path("", views.ruta, name="ruta"),
    path("modulo/<str:modulo_id>/", views.detalle, name="detalle"),
    path("modulo/<str:modulo_id>/empezar/", views.empezar, name="empezar"),
    path("modulo/<str:modulo_id>/dominio/<int:indice>/", views.marcar, name="marcar"),
    path("modulo/<str:modulo_id>/pregunta/<int:indice>/", views.responder, name="responder"),
    path("modulo/<str:modulo_id>/reiniciar/", views.reiniciar, name="reiniciar"),
    path("modulo/<str:modulo_id>/notas/", views.notas, name="notas"),
    path("modulo/<str:modulo_id>/horas/", views.horas, name="horas"),
]
