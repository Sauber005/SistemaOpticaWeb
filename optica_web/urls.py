# SistemaOpticaWeb/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clientes/', include('clientes.urls')),
    path('productos/', include('productos.urls')),
    path('prescripciones/', include('prescripciones.urls')),
    path('ventas/', include('ventas.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]