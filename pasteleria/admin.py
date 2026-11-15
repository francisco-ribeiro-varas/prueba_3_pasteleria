from django.contrib import admin

from .models import Producto
from .templatetags.moneda_chilena import clp


@admin.display(description='Precio')
def precio_clp(obj):
    return clp(obj.precio)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', precio_clp, 'disponible')
    list_filter = ('disponible',)
    search_fields = ('nombre', 'descripcion')
