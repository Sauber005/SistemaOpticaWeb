from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.lista_ventas, name='lista_ventas'),
    path('crear/', views.crear_venta, name='crear_venta'),
    path('<int:pk>/', views.detalle_venta, name='detalle_venta'),
    path('<int:pk>/editar/', views.editar_venta, name='editar_venta'),
    path('<int:pk>/eliminar/', views.eliminar_venta, name='eliminar_venta'),
    path('<int:pk>/pagar-saldo/', views.pagar_saldo_venta, name='pagar_saldo_venta'),
    path('ajax/buscar-productos/', views.buscar_productos_ajax, name='buscar_productos_ajax'),
    path('ajax/buscar-clientes/', views.buscar_clientes_ajax, name='buscar_clientes_ajax'),
    path('<int:pk>/pdf/', views.generar_pdf_venta, name='generar_pdf_venta'),
    # Nueva URL para crear cliente vía AJAX
    path('ajax/crear-cliente/', views.crear_cliente_en_venta, name='crear_cliente_en_venta'),
]