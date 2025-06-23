# prescripciones/urls.py

from django.urls import path
from .views import (
    PrescripcionCreateView,
    PrescripcionListView,
    PrescripcionDetailView,
    PrescripcionUpdateView,
    PrescripcionDeleteView,
    buscar_clientes_ajax_prescripciones, # Vista de búsqueda
    crear_cliente_en_prescripcion # ¡Nueva vista para crear cliente!
)

app_name = 'prescripciones'

urlpatterns = [
    path('nueva/', PrescripcionCreateView.as_view(), name='prescripcion_create'),
    path('', PrescripcionListView.as_view(), name='prescripcion_list'),
    path('<int:pk>/', PrescripcionDetailView.as_view(), name='prescripcion_detail'),
    path('<int:pk>/editar/', PrescripcionUpdateView.as_view(), name='prescripcion_update'),
    path('<int:pk>/eliminar/', PrescripcionDeleteView.as_view(), name='prescripcion_delete'),
    path('ajax/buscar-clientes/', buscar_clientes_ajax_prescripciones, name='buscar_clientes_ajax_prescripciones'),
    path('ajax/crear-cliente/', crear_cliente_en_prescripcion, name='crear_cliente_en_prescripcion'), # ¡Nueva URL!
]