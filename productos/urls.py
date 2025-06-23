# productos/urls.py (CORREGIDO)

from django.urls import path
from . import views

app_name = 'productos' # <-- AÑADIDO: Crucial para los namespaces

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'), # Cambiado a la raíz de la app
    path('agregar/', views.agregar_producto, name='agregar_producto'),
    path('<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
]