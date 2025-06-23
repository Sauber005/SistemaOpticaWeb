from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required # Importar permission_required
from django.db.models import Q

# --- IMPORTACIONES CORRECTAS ---
from .models import Cliente
from .forms import ClienteForm

# --- VISTAS CRUD PARA CLIENTES ---

@login_required
@permission_required('clientes.view_cliente', raise_exception=True) # Requiere permiso para ver clientes
def cliente_list(request):
    """
    Muestra una lista de todos los clientes con funcionalidad de búsqueda.
    """
    queryset = Cliente.objects.all().order_by('apellido_paterno', 'nombre')
    query = request.GET.get('q')

    if query:
        queryset = queryset.filter(
            Q(nombre__icontains=query) |
            Q(apellido_paterno__icontains=query) |
            Q(apellido_materno__icontains=query) |
            Q(telefono__icontains=query)
        ).distinct()
        if not queryset.exists():
            messages.warning(request, f"No se encontraron clientes para la búsqueda '{query}'.")
    
    context = {
        'clientes': queryset,
        'titulo': 'Lista de Clientes',
        'query': query,
    }
    return render(request, 'clientes/cliente_list.html', context)


@login_required
@permission_required('clientes.add_cliente', raise_exception=True) # Requiere permiso para añadir clientes
def cliente_create(request):
    """Maneja la creación de un nuevo cliente."""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado exitosamente.')
            return redirect('cliente_list') 
    else:
        form = ClienteForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Cliente'
    }
    return render(request, 'clientes/cliente_form.html', context)


@login_required
@permission_required('clientes.view_cliente', raise_exception=True) # Requiere permiso para ver detalles del cliente
def cliente_detail(request, pk):
    """Muestra los detalles de un cliente específico."""
    cliente = get_object_or_404(Cliente, pk=pk)
    context = {
        'cliente': cliente,
        'titulo': f'Detalle de {cliente.get_full_name()}'
    }
    return render(request, 'clientes/cliente_detail.html', context)


@login_required
@permission_required('clientes.change_cliente', raise_exception=True) # Requiere permiso para cambiar/editar clientes
def cliente_update(request, pk):
    """Maneja la actualización de un cliente existente."""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente.')
            return redirect('cliente_detail', pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'form': form, 
        'cliente': cliente,
        'titulo': f'Editar Cliente: {cliente.get_full_name()}'
    }
    return render(request, 'clientes/cliente_form.html', context)


@login_required
@permission_required('clientes.delete_cliente', raise_exception=True) # Requiere permiso para eliminar clientes
def cliente_delete(request, pk):
    """Maneja la eliminación de un cliente, mostrando una página de confirmación."""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente_nombre = cliente.get_full_name()
        cliente.delete()
        messages.success(request, f'El cliente {cliente_nombre} ha sido eliminado.')
        return redirect('cliente_list')
    
    context = {
        'cliente': cliente
    }
    return render(request, 'clientes/cliente_confirm_delete.html', context)