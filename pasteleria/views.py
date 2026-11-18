from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PedidoForm
from .models import Pedido, Producto


def inicio(request):
    productos = Producto.objects.all()
    return render(request, 'inicio.html', {'productos': productos})


def detalle_producto(request, producto_id):
    producto = Producto.objects.filter(
        pk=producto_id,
        disponible=True,
        stock__gt=0,
    ).first()
    if producto is None:
        return render(request, '404.html', status=404)

    formulario = PedidoForm(request.POST if request.method == 'POST' else None)
    formulario.fields['cantidad'].widget.attrs['max'] = producto.stock

    if request.method == 'POST':
        if formulario.is_valid():
            cantidad = formulario.cleaned_data['cantidad']
            with transaction.atomic():
                stock_descontado = Producto.objects.filter(
                    pk=producto.pk,
                    disponible=True,
                    stock__gte=cantidad,
                ).update(stock=F('stock') - cantidad)

                if stock_descontado:
                    pedido = formulario.save(commit=False)
                    pedido.producto = producto
                    pedido.producto_nombre = producto.nombre
                    pedido.precio_unitario = producto.precio
                    pedido.save()
                    return redirect('pedido_confirmado', pedido_id=pedido.pk)

                try:
                    producto.refresh_from_db()
                except Producto.DoesNotExist:
                    return render(request, '404.html', status=404)

            if not producto.disponible or producto.stock == 0:
                return render(request, '404.html', status=404)

            formulario.add_error(
                'cantidad',
                f'Solo quedan {producto.stock} unidades disponibles.',
            )
            formulario.fields['cantidad'].widget.attrs['max'] = producto.stock

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
