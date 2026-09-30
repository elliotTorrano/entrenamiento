from django import forms

from .models import Requerimiento
from .reglas import validar_folio


class RequerimientoForm(forms.ModelForm):
    class Meta:
        model = Requerimiento
        fields = ["folio", "dependencia", "proveedor", "descripcion", "monto", "estatus", "fecha", "adjunto"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            clase = "form-select" if isinstance(campo.widget, forms.Select) else "form-control"
            campo.widget.attrs.setdefault("class", clase)

    def clean_monto(self):
        monto = self.cleaned_data["monto"]
        if monto < 0:
            raise forms.ValidationError("El monto no puede ser negativo.")
        return monto

    def clean(self):
        datos = super().clean()
        folio = datos.get("folio")
        dependencia = datos.get("dependencia")
        if folio and dependencia and not validar_folio(folio, dependencia.formato_folio):
            self.add_error(
                "folio",
                f"El folio no cumple el formato de {dependencia}: {dependencia.formato_folio}",
            )
        return datos
