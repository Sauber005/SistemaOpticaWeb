# clientes/models.py
from django.db import models
from datetime import date

class Cliente(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre(s)")
    apellido_paterno = models.CharField(max_length=100, verbose_name="Apellido Paterno")
    apellido_materno = models.CharField(max_length=100, blank=True, null=True, verbose_name="Apellido Materno")
    
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")
    
    telefono = models.CharField(max_length=20, verbose_name="Teléfono Principal")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    telefono2 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono Adicional")
    
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    def __str__(self):
        full_name = f"{self.nombre} {self.apellido_paterno}"
        if self.apellido_materno:
            full_name += f" {self.apellido_materno}"
        return full_name

    def get_full_name(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno or ''}".strip()

    def calcular_edad(self):
        if self.fecha_nacimiento:
            hoy = date.today()
            edad = hoy.year - self.fecha_nacimiento.year
            if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
                edad -= 1
            return edad
        return None

    # MÉTODOS para formatear teléfonos
    def _format_phone_number(self, number_str):
        """Formatea un número de 10 dígitos en XXX-XXXXXXX."""
        # Limpiar cualquier caracter no numérico antes de intentar formatear
        cleaned_number = ''.join(filter(str.isdigit, number_str or ''))
        
        if not cleaned_number or len(cleaned_number) != 10:
            return number_str # Si no es un número válido de 10 dígitos, retorna como está

        # Formato XXX-XXXXXXX
        return f"{cleaned_number[0:3]}-{cleaned_number[3:10]}"

    @property
    def formatted_telefono(self):
        return self._format_phone_number(self.telefono)

    @property
    def formatted_telefono2(self):
        return self._format_phone_number(self.telefono2)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['apellido_paterno', 'apellido_materno', 'nombre']