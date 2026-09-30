from datetime import date
from decimal import Decimal

from django.db import models


class Dependencia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    formato_folio = models.CharField(
        max_length=30, help_text="# = un dígito, AAAA = año. Ejemplo: SSC-####/AAAA"
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    rfc = models.CharField("RFC", max_length=13, unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "proveedores"

    def __str__(self):
        return self.nombre


class Requerimiento(models.Model):
    class Estatus(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        AUTORIZADO = "autorizado", "Autorizado"
        PAGADO = "pagado", "Pagado"
        CANCELADO = "cancelado", "Cancelado"

    folio = models.CharField(max_length=30, unique=True)
    dependencia = models.ForeignKey(
        Dependencia, on_delete=models.PROTECT, related_name="requerimientos"
    )
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.PROTECT, null=True, blank=True
    )
    descripcion = models.TextField("descripción", blank=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    estatus = models.CharField(
        max_length=20, choices=Estatus.choices, default=Estatus.PENDIENTE
    )
    fecha = models.DateField(default=date.today)
    adjunto = models.FileField(upload_to="adjuntos/%Y/", blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha", "folio"]

    def __str__(self):
        return self.folio

    @property
    def monto_efectivo(self):
        if self.estatus == self.Estatus.CANCELADO:
            return Decimal("0")
        return self.monto
