from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from .forms import RegistroForm

@require_http_methods(["GET", "POST"])
def registro(request):
    if request.user.is_authenticated:
        return redirect("cuenta")
    form = RegistroForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tu cuenta fue creada. Ya puedes iniciar sesión.")
        return redirect("login")
    return render(request, "cuentas/registro.html", {"form": form})

@login_required
def cuenta(request):
    return render(request, "cuentas/cuenta.html")
