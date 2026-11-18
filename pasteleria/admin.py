from django.contrib import admin
from django.utils.html import format_html

from .models import Pedido, Producto


@admin.display(description='Precio')
def precio_clp(obj):
    return obj.precio_formateado


@admin.display(description='Imagen')
def imagen_preview(obj):
    if obj.imagen:
        return format_html(
            '<img src="{}" alt="{}" style="width: 64px; height: 64px; object-fit: cover;">',
            obj.imagen.url,
            obj.nombre,
        )
    if obj.imagen_url:
        return format_html(
            '<img src="{}" alt="{}" style="width: 64px; height: 64px; object-fit: cover;">',
            obj.imagen_url,
            obj.nombre,
        )
    return 'Sin imagen'


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', imagen_preview, precio_clp, 'stock', 'disponible')
    list_filter = ('disponible',)
    search_fields = ('nombre', 'descripcion')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto_nombre', 'nombre_cliente', 'cantidad', 'fecha')
    list_filter = ('fecha',)
    search_fields = ('producto_nombre', 'nombre_cliente', 'correo', 'telefono')
    readonly_fields = ('producto', 'producto_nombre', 'precio_unitario', 'cantidad',
                       'nombre_cliente', 'correo', 'telefono', 'fecha')
