from django import forms

from .models import Pedido


class PedidoForm(forms.ModelForm):
    cantidad = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'min': 1}))

    class Meta:
        model = Pedido
        fields = ('nombre_cliente', 'correo', 'telefono', 'cantidad')
        labels = {
            'nombre_cliente': 'Nombre',
            'correo': 'Correo electrónico',
            'telefono': 'Teléfono',
            'cantidad': 'Cantidad',
        }
