# prescripciones/models.py (CORREGIDO)

from django.db import models
from clientes.models import Cliente
from datetime import date
from decimal import Decimal # Importar Decimal para el manejo de los números

class Prescripcion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='prescripciones', verbose_name="Cliente")

    fecha_prescripcion = models.DateField(default=date.today, verbose_name="Fecha de Prescripción")

    # Ojo Derecho (OD)
    esfera_od = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name="Esfera OD")
    cilindro_od = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name="Cilindro OD")
    eje_od = models.IntegerField(blank=True, null=True, verbose_name="Eje OD")
    adicion_od = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name="Adición OD")
    prisma_od = models.CharField(max_length=50, blank=True, null=True, verbose_name="Prisma OD")
    base_od = models.CharField(max_length=50, blank=True, null=True, verbose_name="Base OD")

    # Ojo Izquierdo (OI)
    esfera_oi = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name="Esfera OI")
    cilindro_oi = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name="Cilindro OI")
    eje_oi = models.IntegerField(blank=True, null=True, verbose_name="Eje OI")
    adicion_oi = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name="Adición OI")
    prisma_oi = models.CharField(max_length=50, blank=True, null=True, verbose_name="Prisma OI")
    base_oi = models.CharField(max_length=50, blank=True, null=True, verbose_name="Base OI")

    dnp_od = models.PositiveIntegerField(blank=True, null=True, verbose_name="DNP OD (mm)")
    dnp_oi = models.PositiveIntegerField(blank=True, null=True, verbose_name="DNP OI (mm)")

    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Prescripción"
        verbose_name_plural = "Prescripciones"
        ordering = ['-fecha_prescripcion', 'cliente__apellido_paterno']

    def __str__(self):
        return f"Prescripción de {self.cliente.nombre} {self.cliente.apellido_paterno} - {self.fecha_prescripcion}"

    # --- INICIO DE LA NUEVA SECCIÓN DE FORMATO ---
    
    def _format_decimal_with_sign(self, value):
        """Función interna para formatear un valor Decimal."""
        if value is None:
            return "-"
        
        # Asegurarnos de que estamos trabajando con un objeto Decimal
        value = Decimal(value)

        if value > 0:
            return f"+{value:.2f}"
        else:
            return f"{value:.2f}"

    @property
    def formatted_esfera_od(self):
        return self._format_decimal_with_sign(self.esfera_od)

    @property
    def formatted_esfera_oi(self):
        return self._format_decimal_with_sign(self.esfera_oi)
        
    @property
    def formatted_adicion_od(self):
        return self._format_decimal_with_sign(self.adicion_od)

    @property
    def formatted_adicion_oi(self):
        return self._format_decimal_with_sign(self.adicion_oi)

    # --- FIN DE LA NUEVA SECCIÓN ---