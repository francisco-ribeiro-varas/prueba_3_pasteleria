from django.shortcuts import render

from .models import Producto


def inicio(request):
    productos = Producto.objects.filter(disponible=True)
    return render(request, 'inicio.html', {'productos': productos})


def pagina_no_encontrada(request, exception):
    return render(request, '404.html', status=404)
