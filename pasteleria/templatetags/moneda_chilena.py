from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def clp(value):
    try:
        numero = Decimal(str(value))
    except (TypeError, ValueError, InvalidOperation):
        return value

    if numero == numero.to_integral_value():
        return f"$ {numero.quantize(Decimal('1')):,.0f}".replace(",", ".")

    numero = numero.quantize(Decimal('0.01'))
    texto = f"{numero:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"$ {texto}"
