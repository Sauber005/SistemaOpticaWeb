from django import forms
from django.forms import inlineformset_factory
from .models import Venta, DetalleVenta
from clientes.models import Cliente
from productos.models import Producto
from decimal import Decimal

METODO_PAGO_CHOICES = [
    ('Efectivo', 'Efectivo'), ('Tarjeta de Débito', 'Tarjeta de Débito'), ('Tarjeta de Crédito', 'Tarjeta de Crédito'),
    ('Transferencia SPEI', 'Transferencia SPEI'), ('Mercado Pago', 'Mercado Pago'), ('Otro', 'Otro'),
]

class VentaForm(forms.ModelForm):
    # Añadimos una opción para cliente genérico al queryset y lo hacemos NO requerido en el form
    # La validación se hará en la vista.
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all().order_by('nombre', 'apellido_paterno'),
        required=False, # Hacemos que NO sea requerido a nivel de formulario
        label="Cliente",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Seleccionar Cliente (Opcional) --" # Etiqueta para la opción nula
    )

    # Campo oculto para indicar si es una venta de mostrador (lo controlaremos en JS)
    es_venta_mostrador = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Venta
        fields = ['cliente', 'metodo_pago', 'observaciones', 'total_venta', 'pagado', 'cambio', 'es_venta_mostrador'] # Añadir es_venta_mostrador
        widgets = {
            'metodo_pago': forms.Select(choices=METODO_PAGO_CHOICES, attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'pagado': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_venta': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'cambio': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
        }

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control producto-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control cantidad-input', 'min': '1'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control precio-unitario-input', 'readonly': True}),
        }

DetalleVentaFormSet = inlineformset_factory(
    Venta, DetalleVenta, form=DetalleVentaForm, extra=1, can_delete=True, min_num=1, validate_min=True
)

class PagoSaldoForm(forms.Form):
    monto_a_pagar = forms.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'), label="Monto a Abonar")