# productos/models.py

from django.db import models

class Producto(models.Model):
    TIPOS_PRODUCTO = [
        ('armazon', 'Armazón'),
        ('lente_contacto', 'Lente de Contacto'),
        ('lente_graduado', 'Lente Graduado'), # Campo especial, no tiene stock físico real
        ('accesorio', 'Accesorio'),
        ('solucion', 'Solución'),
        ('servicio', 'Servicio') # No tiene stock físico real
    ]

    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    marca = models.CharField(max_length=100, blank=True, null=True, verbose_name="Marca")
    tipo = models.CharField(max_length=50, choices=TIPOS_PRODUCTO, default='armazon', verbose_name="Tipo de Producto")
    codigo_barras = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Código de Barras")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Precio de Compra")
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de Venta")
    stock = models.IntegerField(default=0, verbose_name="Stock")
    fecha_ingreso = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Ingreso")
    # Agregamos este campo para mantener un registro de la última actualización, útil para auditoría
    ultima_actualizacion = models.DateTimeField(auto_now=True) 
    activo = models.BooleanField(default=True, verbose_name="Activo") # Para activar/desactivar un producto

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre', 'marca'] # Tu ordenación es buena

    def __str__(self):
        return f"{self.nombre} ({self.marca or 'N/A'}) - {self.tipo}"

    @property
    def requiere_stock(self):
        return self.tipo not in ['servicio', 'lente_graduado']