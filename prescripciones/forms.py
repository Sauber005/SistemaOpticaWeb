from django import forms
from .models import Prescripcion
from clientes.models import Cliente

class PrescripcionForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all().order_by('nombre', 'apellido_paterno'),
        required=True,
        label="Cliente",
        widget=forms.Select(attrs={'class': 'form-control cliente-select2'}),
        help_text="Busca un cliente por nombre o apellidos."
    )

    class Meta:
        model = Prescripcion
        # --- ORDEN DE CAMPOS CORREGIDO ---
        fields = [
            'cliente', 
            'esfera_od', 'cilindro_od', 'eje_od', 'dnp_od', # dnp_od movido aquí
            'adicion_od', 'prisma_od', 'base_od',
            'esfera_oi', 'cilindro_oi', 'eje_oi', 'dnp_oi', # dnp_oi movido aquí
            'adicion_oi', 'prisma_oi', 'base_oi',
            'observaciones'
        ]
        
        widgets = {
            # Se eliminó la entrada para 'fecha_prescripcion' para que sea automática
            'observaciones': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'esfera_od': forms.NumberInput(attrs={'step': '0.25', 'class': 'form-control'}),
            'cilindro_od': forms.NumberInput(attrs={'step': '0.25', 'class': 'form-control'}),
            'eje_od': forms.NumberInput(attrs={'class': 'form-control'}),
            'adicion_od': forms.NumberInput(attrs={'step': '0.25', 'class': 'form-control'}),
            'prisma_od': forms.TextInput(attrs={'class': 'form-control'}),
            'base_od': forms.TextInput(attrs={'class': 'form-control'}),
            'esfera_oi': forms.NumberInput(attrs={'step': '0.25', 'class': 'form-control'}),
            'cilindro_oi': forms.NumberInput(attrs={'step': '0.25', 'class': 'form-control'}),
            'eje_oi': forms.NumberInput(attrs={'class': 'form-control'}),
            'adicion_oi': forms.NumberInput(attrs={'step': '0.25', 'class': 'form-control'}),
            'prisma_oi': forms.TextInput(attrs={'class': 'form-control'}),
            'base_oi': forms.TextInput(attrs={'class': 'form-control'}),
            'dnp_od': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '99'}),
            'dnp_oi': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '99'}),
        }

        labels = {
            'cliente': 'Cliente',
            'esfera_od': 'Esfera OD',
            'cilindro_od': 'Cilindro OD',
            'eje_od': 'Eje OD (°)',
            'adicion_od': 'Adición OD',
            'prisma_od': 'Prisma OD',
            'base_od': 'Base OD',
            'esfera_oi': 'Esfera OI',
            'cilindro_oi': 'Cilindro OI',
            'eje_oi': 'Eje OI (°)',
            'adicion_oi': 'Adición OI',
            'prisma_oi': 'Prisma OI',
            'base_oi': 'Base OI',
            'dnp_od': 'DNP OD (mm)',
            'dnp_oi': 'DNP OI (mm)',
            'observaciones': 'Observaciones Adicionales',
        }