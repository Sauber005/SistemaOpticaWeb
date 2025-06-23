# ventas/admin.py
from django.contrib import admin
from .models import Venta, DetalleVenta # Importa tus nuevos modelos

# Registra tus modelos aquí.
admin.site.register(Venta)
admin.site.register(DetalleVenta)