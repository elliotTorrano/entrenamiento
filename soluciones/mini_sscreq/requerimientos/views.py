from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import RequerimientoForm
from .models import Dependencia, Requerimiento


def lista(request):
    requerimientos = Requerimiento.objects.select_related("dependencia", "proveedor")

    estatus = request.GET.get("estatus", "")
    dependencia = request.GET.get("dependencia", "")
    q = request.GET.get("q", "").strip()
    if estatus:
        requerimientos = requerimientos.filter(estatus=estatus)
    if dependencia:
        requerimientos = requerimientos.filter(dependencia_id=dependencia)
    if q:
        requerimientos = requerimientos.filter(
            Q(folio__icontains=q) | Q(descripcion__icontains=q)
        )

    pagina = Paginator(requerimientos, 20).get_page(request.GET.get("page"))
    contexto = {
        "pagina": pagina,
        "estatus_opciones": Requerimiento.Estatus.choices,
        "dependencias": Dependencia.objects.all(),
        "filtros": {"estatus": estatus, "dependencia": dependencia, "q": q},
    }
    if request.htmx:
        return render(request, "requerimientos/_tabla.html", contexto)
    return render(request, "requerimientos/lista.html", contexto)


def formulario(request, pk=None):
    requerimiento = get_object_or_404(Requerimiento, pk=pk) if pk else None
    form = RequerimientoForm(
        request.POST or None, request.FILES or None, instance=requerimiento
    )
    if request.method == "POST" and form.is_valid():
        guardado = form.save()
        if request.htmx:
            return HttpResponse(status=204, headers={"HX-Trigger": "requerimiento-guardado"})
        messages.success(request, f"Requerimiento {guardado.folio} guardado.")
        return redirect("requerimientos:lista")

    contexto = {"form": form, "requerimiento": requerimiento}
    if request.htmx:
        return render(request, "requerimientos/_form_modal.html", contexto)
    return render(request, "requerimientos/formulario.html", contexto)


@require_POST
def cambiar_estatus(request, pk):
    requerimiento = get_object_or_404(Requerimiento, pk=pk)
    nuevo = request.POST.get("estatus")
    if nuevo in Requerimiento.Estatus.values:
        requerimiento.estatus = nuevo
        requerimiento.save(update_fields=["estatus", "modificado"])
    return render(
        request,
        "requerimientos/_fila.html",
        {"r": requerimiento, "estatus_opciones": Requerimiento.Estatus.choices},
    )


@require_POST
def borrar(request, pk):
    requerimiento = get_object_or_404(Requerimiento, pk=pk)
    requerimiento.delete()
    if request.htmx:
        return HttpResponse("")
    messages.success(request, f"Requerimiento {requerimiento.folio} borrado.")
    return redirect("requerimientos:lista")
