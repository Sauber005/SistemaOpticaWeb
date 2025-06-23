# prescripciones/admin.py
from django.contrib import admin
from .models import Prescripcion # Importa tu modelo Prescripcion

# Registra tu modelo Prescripcion aquí.
admin.site.register(Prescripcion)