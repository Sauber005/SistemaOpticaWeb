from django import forms
from .models import Cliente
import re

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        # ¡IMPORTANTE! Define el orden de los campos aquí
        fields = [
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'fecha_nacimiento',
            'telefono',  # Teléfono 1
            'telefono2', # Teléfono 2 (uno después del otro)
            'email',
            'direccion',
            'observaciones'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_paterno': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_materno': forms.TextInput(attrs={'class': 'form-control'}),
            # Asegúrate de que 'tel-mask' esté incluido en la clase de ambos campos de teléfono
            'telefono': forms.TextInput(attrs={'class': 'form-control tel-mask', 'placeholder': 'Ej. 686-123-4567'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono2': forms.TextInput(attrs={'class': 'form-control tel-mask', 'placeholder': 'Ej. 686-765-4321'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'nombre': 'Nombre(s)',
            'apellido_paterno': 'Apellido Paterno',
            'apellido_materno': 'Apellido Materno',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'telefono': 'Teléfono Principal',
            'email': 'Email',
            'telefono2': 'Teléfono Adicional',
            'direccion': 'Dirección',
            'observaciones': 'Observaciones',
        }

    # Métodos clean_telefono y clean_telefono2 (sin cambios, ya manejan guiones en el backend)
    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if telefono:
            telefono_limpio = re.sub(r'[\s-]', '', telefono)
            if not telefono_limpio.isdigit() or len(telefono_limpio) != 10:
                raise forms.ValidationError("El teléfono principal debe contener 10 dígitos (solo números, guiones y espacios son permitidos).")
            return telefono_limpio
        return telefono

    def clean_telefono2(self):
        telefono2 = self.cleaned_data['telefono2']
        if telefono2:
            telefono_limpio = re.sub(r'[\s-]', '', telefono2)
            if not telefono_limpio.isdigit() or len(telefono_limpio) != 10:
                raise forms.ValidationError("El teléfono adicional debe contener 10 dígitos (solo números, guiones y espacios son permitidos).")
            return telefono_limpio
        return telefono2