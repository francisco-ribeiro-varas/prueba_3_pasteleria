from django.shortcuts import get_object_or_404, redirect, render

from .forms import PedidoForm
from .models import Pedido, Producto


def inicio(request):
    productos = Producto.objects.all()
    return render(request, 'inicio.html', {'productos': productos})


def detalle_producto(request, producto_id):
    producto = Producto.objects.filter(pk=producto_id).first()
    if producto is None or not producto.disponible:
        return render(request, '404.html', status=404)

    if request.method == 'POST':
        formulario = PedidoForm(request.POST)
        if formulario.is_valid():
            pedido = formulario.save(commit=False)
            pedido.producto = producto
            pedido.producto_nombre = producto.nombre
            pedido.precio_unitario = producto.precio
            pedido.save()
            return redirect('pedido_confirmado', pedido_id=pedido.pk)
    else:
        formulario = PedidoForm()

    return render(
        request,
        'producto.html',
        {'producto': producto, 'formulario': formulario},
    )


def pedido_confirmado(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    return render(request, 'pedido_confirmado.html', {'pedido': pedido})


def pagina_no_encontrada(request, exception):
    return render(request, '404.html', status=404)
