from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.urls import reverse
from decimal import Decimal
from django.views.decorators.http import require_POST

# --- Importaciones de Modelos ---
from .models import Venta, DetalleVenta
from clientes.models import Cliente
from productos.models import Producto

# --- Importaciones de Formularios ---
from .forms import VentaForm, DetalleVentaFormSet, PagoSaldoForm
from clientes.forms import ClienteForm # Asegúrate de que ClienteForm esté importado

# --- Importaciones para WeasyPrint ---
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
import os
from django.conf import settings

# --- VISTAS DEL MÓDULO DE VENTAS ---

@login_required
@permission_required('ventas.view_venta', raise_exception=True)
def lista_ventas(request):
    ventas_list = Venta.objects.select_related('cliente').all().order_by('-fecha_venta')
    query = request.GET.get('q')
    if query:
        ventas_list = ventas_list.filter(
            Q(id__icontains=query) |
            Q(cliente__nombre__icontains=query) |
            Q(cliente__apellido_paterno__icontains=query)
        ).distinct()
        if not ventas_list.exists(): # Mensaje si la búsqueda no encuentra resultados
            messages.warning(request, f"No se encontraron ventas para la búsqueda '{query}'.")
    context = {'titulo': 'Lista de Ventas', 'ventas': ventas_list, 'query': query}
    return render(request, 'ventas/lista_ventas.html', context)


@login_required
@permission_required('ventas.view_venta', raise_exception=True)
def detalle_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    context = {'titulo': f'Detalle de Venta #{venta.pk}', 'venta': venta}
    return render(request, 'ventas/detalle_venta.html', context)


@login_required
@permission_required('ventas.add_venta', raise_exception=True)
def crear_venta(request):
    if request.method == 'POST':
        form_venta = VentaForm(request.POST)
        formset = DetalleVentaFormSet(request.POST)

        if form_venta.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    venta = form_venta.save(commit=False) # No guardar aún
                    
                    # Lógica para Venta de Mostrador
                    # El campo oculto 'es_venta_mostrador' del VentaForm indica si el checkbox fue marcado
                    es_venta_mostrador = form_venta.cleaned_data.get('es_venta_mostrador')
                    if es_venta_mostrador:
                        # Si es venta de mostrador, asegurar que el cliente sea None
                        venta.cliente = None
                    # Si no es venta de mostrador y el cliente no fue seleccionado, levantar un error
                    # (Esto maneja el caso donde el checkbox no está marcado pero el campo cliente está vacío)
                    elif not venta.cliente: 
                        raise ValueError("Debe seleccionar un cliente para la venta o marcarla como 'Venta de Mostrador'.")

                    venta.save()
                    formset.instance = venta
                    formset.save()
                
                # *** Lógica de impresión ***
                submit_and_print = request.POST.get('submit_and_print') == 'true'

                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    response_data = {
                        'success': True,
                        'message': f'Venta #{venta.pk} creada exitosamente.',
                        'redirect_url': reverse('ventas:detalle_venta', kwargs={'pk': venta.pk})
                    }
                    if submit_and_print:
                        response_data['print_url'] = reverse('ventas:generar_pdf_venta', kwargs={'pk': venta.pk})
                    return JsonResponse(response_data)
                
                messages.success(request, f'Venta #{venta.pk} creada exitosamente.')
                return redirect('ventas:detalle_venta', pk=venta.pk)

            except ValueError as e: # Captura errores lógicos como cliente no seleccionado
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': str(e)}, status=400) # Devolver 400 Bad Request
                messages.error(request, str(e))
            except Exception as e: # Captura cualquier otra excepción inesperada
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': f"Ocurrió un error al guardar la venta: {e}"}, status=500)
                messages.error(request, f"Ocurrió un error inesperado: {e}")

        else: # Formulario no válido (errores de validación de Django)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Esto es crucial para mostrar errores específicos de campo en el frontend
                errors_dict = {}
                for field, field_errors in form_venta.errors.items():
                    errors_dict[field] = [str(e) for e in field_errors]
                
                formset_errors_list = []
                for form_errs in formset.errors:
                    if form_errs: # Solo si el formulario individual del formset tiene errores
                        formset_errors_list.append({field: [str(e) for e in field_errors] for field, field_errors in form_errs.items()})

                return JsonResponse({
                    'success': False,
                    'error': 'Por favor, corrige los errores en el formulario.',
                    'errors': errors_dict, # Errores de VentaForm
                    'formset_errors': formset_errors_list # Errores de DetalleVentaFormSet (lista de diccionarios)
                }, status=400)
            messages.error(request, 'Por favor, corrige los errores en el formulario.')

    else: # Petición GET: Inicialización de formularios
        initial_data = {}
        cliente_id = request.GET.get('cliente_id')
        if cliente_id:
            try:
                initial_data['cliente'] = Cliente.objects.get(pk=cliente_id)
            except Cliente.DoesNotExist:
                messages.warning(request, f"El cliente con ID {cliente_id} no fue encontrado.")
        
        form_venta = VentaForm(initial=initial_data)
        formset = DetalleVentaFormSet()
    
    # Instancia del ClienteForm para el modal de "Agregar Nuevo Cliente"
    form_cliente_modal = ClienteForm() 

    context = {
        'titulo': 'Crear Nueva Venta',
        'form_venta': form_venta,
        'formset': formset,
        'form_cliente_modal': form_cliente_modal # Pasa el formulario del cliente al contexto
    }
    return render(request, 'ventas/venta_form.html', context)


@login_required
@permission_required('ventas.change_venta', raise_exception=True)
def editar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        form_venta = VentaForm(request.POST, instance=venta)
        formset = DetalleVentaFormSet(request.POST, instance=venta)
        if form_venta.is_valid() and formset.is_valid():
            with transaction.atomic():
                form_venta.save()
                formset.save()
            messages.success(request, f'Venta #{venta.pk} actualizada exitosamente.')
            return redirect('ventas:detalle_venta', pk=venta.pk)
    else:
        form_venta = VentaForm(instance=venta)
        formset = DetalleVentaFormSet(instance=venta)
    
    # También pasa un ClienteForm para el modal, aunque no sea el foco principal de la edición
    form_cliente_modal = ClienteForm() 
    
    context = {
        'titulo': f'Editar Venta #{venta.pk}',
        'form_venta': form_venta,
        'formset': formset,
        'form_cliente_modal': form_cliente_modal # Pasa el formulario del cliente al contexto
    }
    return render(request, 'ventas/venta_form.html', context)


@login_required
@permission_required('ventas.delete_venta', raise_exception=True)
def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        venta_id = venta.pk
        venta.delete()
        messages.success(request, f'La venta #{venta_id} ha sido eliminada exitosamente.')
        return redirect('ventas:lista_ventas')
    
    context = {'titulo': f'Confirmar Eliminación de Venta #{venta.pk}', 'venta': venta}
    return render(request, 'ventas/venta_confirm_delete.html', context)


@login_required
@permission_required('ventas.change_venta', raise_exception=True) # Se requiere permiso de cambio para pagar
def pagar_saldo_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)

    if venta.esta_pagada:
        messages.info(request, "Esta venta ya está completamente pagada.")
        return redirect('ventas:detalle_venta', pk=venta.pk)

    if request.method == 'POST':
        form = PagoSaldoForm(request.POST)
        if form.is_valid():
            monto_adicional = form.cleaned_data['monto_a_pagar']
            
            # Verificamos que el abono no exceda el saldo pendiente
            if monto_adicional > venta.saldo_pendiente + Decimal('0.01'): # Pequeño margen para errores de decimales
                error_message = f"El monto a pagar (${monto_adicional}) no puede ser mayor que el saldo pendiente (${venta.saldo_pendiente:.2f})."
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': error_message}, status=400)
                messages.error(request, error_message)
            else:
                venta.pagado += monto_adicional
                venta.save()
                success_message = f"Se ha abonado ${monto_adicional:.2f} a la venta."

                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True, 
                        'message': success_message,
                        'redirect_url': reverse('ventas:detalle_venta', kwargs={'pk': venta.pk})
                    })

                messages.success(request, success_message)
                return redirect('ventas:detalle_venta', pk=pk)
        else:
            # Si el formulario no es válido
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors_dict = {field: [str(e) for e in field_errors] for field, field_errors in form.errors.items()}
                return JsonResponse({'success': False, 'errors': errors_dict}, status=400)
            messages.error(request, 'Por favor, corrige los errores en el formulario de pago.')

    else: # Petición GET
        form = PagoSaldoForm(initial={'monto_a_pagar': venta.saldo_pendiente})

    context = {
        'titulo': f'Pagar Saldo de Venta #{venta.pk}',
        'venta': venta,
        'form': form,
    }
    return render(request, 'ventas/pagar_saldo_venta.html', context)


@login_required
@permission_required('productos.view_producto', raise_exception=True)
def buscar_productos_ajax(request):
    query = request.GET.get('q', '')
    productos = Producto.objects.filter(
        Q(nombre__icontains=query) | Q(marca__icontains=query) | Q(codigo_barras__icontains=query)
    ).filter(activo=True)[:20]
    results = [{'id': p.id, 'text': f"{p.nombre} - ${p.precio_venta:.2f}", 'precio_unitario': str(p.precio_venta)} for p in productos]
    return JsonResponse({'results': results})


@login_required
@permission_required('clientes.view_cliente', raise_exception=True)
def buscar_clientes_ajax(request):
    query = request.GET.get('q', '')
    # Permite buscar por ID si se pasa 'id' en el GET (para Select2 cuando ya hay un valor seleccionado)
    cliente_id = request.GET.get('id')
    
    if cliente_id:
        try:
            cliente = Cliente.objects.get(pk=cliente_id)
            results = [{'id': cliente.id, 'text': cliente.get_full_name()}]
        except Cliente.DoesNotExist:
            results = []
    else:
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=query) | Q(apellido_paterno__icontains=query) | Q(telefono__icontains=query)
        )[:20]
        results = [{'id': c.id, 'text': c.get_full_name()} for c in clientes]
    return JsonResponse({'results': results})


@login_required
@permission_required('clientes.add_cliente', raise_exception=True)
@require_POST
def crear_cliente_en_venta(request):
    form = ClienteForm(request.POST)
    if form.is_valid():
        cliente = form.save()
        return JsonResponse({
            'success': True,
            'message': f'Cliente {cliente.get_full_name()} creado exitosamente.',
            'cliente_id': cliente.pk,
            'cliente_text': cliente.get_full_name() # Para Select2
        })
    else:
        # Devolver los errores del formulario para que el frontend los muestre
        # Crispy Forms espera los errores como un diccionario donde las claves son los nombres de los campos
        # y los valores son listas de strings de mensajes de error.
        errors_dict = {field: [str(e) for e in field_errors] for field, field_errors in form.errors.items()}
        return JsonResponse({'success': False, 'errors': errors_dict}, status=400)


@login_required
@permission_required('ventas.view_venta', raise_exception=True) # Permiso para ver la venta al generar PDF
def generar_pdf_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)

    context = {
        'venta': venta,
        'detalles': venta.detalles.all(),
    }

    html_string = render_to_string('ventas/venta_pdf_template.html', context)
    html = HTML(string=html_string)

    css_path = os.path.join(settings.BASE_DIR, 'static', 'css', 'pdf_styles.css')
    stylesheets = []
    if os.path.exists(css_path):
        stylesheets.append(CSS(filename=css_path))

    pdf = html.write_pdf(stylesheets=stylesheets)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="venta_{venta.pk}.pdf"'
    return response