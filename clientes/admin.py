# clientes/admin.py
from django.contrib import admin
from .models import Cliente # Importa tu modelo Cliente

# Registra tu modelo Cliente aquí.
admin.site.register(Cliente)