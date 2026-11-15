from django.contrib import admin
from django.utils.html import format_html

from .models import Producto


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
    list_display = ('nombre', imagen_preview, precio_clp, 'disponible')
    list_filter = ('disponible',)
    search_fields = ('nombre', 'descripcion')
