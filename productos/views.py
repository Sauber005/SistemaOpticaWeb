# productos/views.py (CORREGIDO)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Producto
from .forms import ProductoForm
from django.contrib.auth.decorators import login_required # Recomendado añadir

# NOTA: He añadido el decorador @login_required a todas las vistas por seguridad.

@login_required
def lista_productos(request):
    productos = Producto.objects.all().order_by('nombre', 'marca')

    query = request.GET.get('q')
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(marca__icontains=query) |
            Q(codigo_barras__icontains=query)
        ).distinct()
        if not productos.exists():
            messages.warning(request, f'No se encontraron productos para la búsqueda "{query}".')

    context = {
        'productos': productos,
        'titulo': 'Lista de Productos'
    }
    return render(request, 'productos/lista_productos.html', context)

@login_required
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Producto agregado exitosamente!')
            # --- CORRECCIÓN AQUÍ ---
            return redirect('productos:lista_productos')
    else:
        form = ProductoForm()
    
    context = {
        'form': form,
        'titulo': 'Agregar Nuevo Producto'
    }
    return render(request, 'productos/producto_form.html', context)

@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.info(request, 'Producto actualizado correctamente.')
            # --- CORRECCIÓN AQUÍ ---
            return redirect('productos:lista_productos')
    else:
        form = ProductoForm(instance=producto)

    context = {
        'form': form,
        'titulo': f'Editar Producto: {producto.nombre}'
    }
    return render(request, 'productos/producto_form.html', context)


@login_required
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    context = {
        'producto': producto,
        'titulo': f'Detalle de {producto.nombre}'
    }
    return render(request, 'productos/detalle_producto.html', context)

@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto_nombre = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{producto_nombre}" eliminado exitosamente.')
        # --- CORRECCIÓN AQUÍ ---
        return redirect('productos:lista_productos')
    
    context = {
        'producto': producto,
        'titulo': f'Confirmar Eliminación de {producto.nombre}'
    }
    return render(request, 'productos/producto_confirm_delete.html', context)