# clientes/urls.py

from django.urls import path
from . import views # Importamos el módulo views completo

urlpatterns = [
    # URL para la lista de clientes
    path('', views.cliente_list, name='cliente_list'), 

    # URL para crear un nuevo cliente
    path('nueva/', views.cliente_create, name='cliente_create'),

    # URL para ver los detalles de un cliente específico
    path('<int:pk>/', views.cliente_detail, name='cliente_detail'),

    # URL para editar un cliente existente
    path('<int:pk>/editar/', views.cliente_update, name='cliente_update'),

    # URL para eliminar un cliente
    path('<int:pk>/eliminar/', views.cliente_delete, name='cliente_delete'),
]