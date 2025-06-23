from django.db import models
from django.db.models import Sum
from clientes.models import Cliente
from productos.models import Producto
from django.utils import timezone
from decimal import Decimal

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    fecha_venta = models.DateTimeField(default=timezone.now)
    metodo_pago = models.CharField(max_length=50, blank=True, null=True)
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    pagado = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    cambio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_venta']
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"


    @property
    def saldo_pendiente(self):
        return self.total_venta - self.pagado

    @property
    def esta_pagada(self):
        return self.saldo_pendiente <= 0

    def recalcular_total(self):
        # Suma los subtotales de todos los detalles de venta asociados
        total = self.detalles.aggregate(total_sum=Sum('_subtotal_calculated'))['total_sum'] or Decimal('0.00')
        self.total_venta = total
        
        # Recalcula el cambio
        if self.pagado and self.pagado > self.total_venta:
            self.cambio = self.pagado - self.total_venta
        else:
            self.cambio = Decimal('0.00')

    def __str__(self):
        cliente_info = self.cliente.get_full_name() if self.cliente else "Mostrador"
        return f"Venta #{self.pk} - {cliente_info} - {self.fecha_venta.strftime('%d/%m/%Y %H:%M')}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, verbose_name="Producto")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    _subtotal_calculated = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"


    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def save(self, *args, **kwargs):
        # Calcula y guarda el subtotal antes de guardar el DetalleVenta
        self._subtotal_calculated = self.subtotal
        super().save(*args, **kwargs)
        # Después de guardar el detalle, recalcula el total de la venta asociada
        venta_obj = self.venta
        venta_obj.recalcular_total()
        venta_obj.save()

    def delete(self, *args, **kwargs):
        # Antes de eliminar el detalle, obtener la venta para recalcular después
        venta_obj = self.venta
        super().delete(*args, **kwargs)
        # Después de eliminar el detalle, recalcula el total de la venta asociada
        venta_obj.recalcular_total()
        venta_obj.save()

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre if self.producto else 'Producto Eliminado'}"