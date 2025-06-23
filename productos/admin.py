# productos/admin.py
from django.contrib import admin
from .models import Producto # Solo importamos Producto

admin.site.register(Producto) # Solo registramos Producto

# Si quieres personalizar cómo se ve el producto en el admin, puedes hacer esto (opcional):
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'marca', 'tipo', 'precio_venta', 'stock', 'activo', 'ultima_actualizacion')
    list_filter = ('tipo', 'marca', 'activo')
    search_fields = ('nombre', 'marca', 'codigo_barras', 'descripcion')
    date_hierarchy = 'fecha_ingreso'
    ordering = ('nombre', 'marca')
    readonly_fields = ('fecha_ingreso', 'ultima_actualizacion') # Estos campos solo se muestran, no se editan

admin.site.unregister(Producto) # Desregistra el modelo si ya lo habías registrado antes de personalizarlo
admin.site.register(Producto, ProductoAdmin) # Registra el modelo con la configuración personalizada