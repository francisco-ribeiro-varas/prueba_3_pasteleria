from django.db import models


class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', blank=True)
    imagen_url = models.URLField(blank=True)
    stock = models.PositiveIntegerField(default=0, verbose_name='unidades en stock')
    disponible = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'producto'
        verbose_name_plural = 'productos'

    @property
    def precio_formateado(self):
        if self.precio == self.precio.to_integral_value():
            return f"$ {self.precio:,.0f}".replace(',', '.')

        texto = f'{self.precio:,.2f}'
        texto = texto.replace(',', 'X').replace('.', ',').replace('X', '.')
        return f'$ {texto}'

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos',
    )
    producto_nombre = models.CharField(max_length=120)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    cantidad = models.PositiveIntegerField()
    nombre_cliente = models.CharField(max_length=120)
    correo = models.EmailField()
    telefono = models.CharField(max_length=30)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pedido #{self.pk} - {self.producto_nombre}'
