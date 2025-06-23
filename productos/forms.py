from django import forms
from .models import Producto # Importa tu modelo Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'marca',
            'tipo',
            'codigo_barras',
            'descripcion',
            'precio_compra',
            'precio_venta',
            'stock',
            'activo'
        ]
        # Puedes personalizar los labels si quieres que se vean diferentes en el formulario
        labels = {
            'nombre': 'Nombre del Producto',
            'marca': 'Marca',
            'tipo': 'Tipo de Producto',
            'codigo_barras': 'Código de Barras',
            'descripcion': 'Descripción',
            'precio_compra': 'Precio de Compra',
            'precio_venta': 'Precio de Venta',
            'stock': 'Stock',
            'activo': 'Producto Activo'
        }
        # Widgets opcionales para personalizar la apariencia de los campos
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}), # Hace el textarea más pequeño
            'tipo': forms.Select(attrs={'class': 'form-select'}), # Estilo Bootstrap para select
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}) # Estilo Bootstrap para checkbox
        }