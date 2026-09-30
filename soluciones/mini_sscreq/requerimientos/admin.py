from django.contrib import admin

from .models import Dependencia, Proveedor, Requerimiento


@admin.register(Dependencia)
class DependenciaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "formato_folio"]


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ["nombre", "rfc"]
    search_fields = ["nombre", "rfc"]


@admin.register(Requerimiento)
class RequerimientoAdmin(admin.ModelAdmin):
    list_display = ["folio", "dependencia", "proveedor", "monto", "estatus", "fecha"]
    list_filter = ["estatus", "dependencia"]
    search_fields = ["folio", "descripcion"]
    date_hierarchy = "fecha"
