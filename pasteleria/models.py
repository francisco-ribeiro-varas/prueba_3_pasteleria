from django.db import models


class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', blank=True)
    imagen_url = models.URLField(blank=True)
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
