# prescripciones/views.py

from django.views.generic import (
    CreateView, ListView, DetailView, UpdateView, DeleteView
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, AccessMixin
from django.contrib.auth.decorators import login_required, permission_required
from .models import Prescripcion
from .forms import PrescripcionForm
from clientes.models import Cliente
from clientes.forms import ClienteForm
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from datetime import date
from django.views.decorators.http import require_POST

# Mixin personalizado para controlar la edición de la fecha
class FechaPrescripcionPermisoMixin(AccessMixin):
    """
    Mixin para controlar si el campo fecha_prescripcion es editable.
    Solo Admins y Gerentes pueden editarlo.
    """
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Si el usuario NO es superusuario, admin, o gerente, hacer el campo readonly
        if not self.request.user.is_superuser and not self.request.user.groups.filter(name__in=['Admin', 'Gerente']).exists():
            form.fields['fecha_prescripcion'].widget.attrs['readonly'] = True
            form.fields['fecha_prescripcion'].help_text = "Solo administradores o gerentes pueden modificar esta fecha."
        return form


# --- Vista para Crear una Prescripción ---
class PrescripcionCreateView(LoginRequiredMixin, PermissionRequiredMixin, FechaPrescripcionPermisoMixin, CreateView):
    model = Prescripcion
    form_class = PrescripcionForm
    template_name = 'prescripciones/prescripcion_form.html'
    permission_required = 'prescripciones.add_prescripcion'
    raise_exception = True

    def get_success_url(self):
        # CORRECCIÓN 1 de 3
        return reverse_lazy('prescripciones:prescripcion_detail', kwargs={'pk': self.object.pk})

    def get_initial(self):
        initial = super().get_initial()
        cliente_id = self.request.GET.get('cliente_id')
        if cliente_id:
            initial['cliente'] = cliente_id
        initial['fecha_prescripcion'] = date.today() # Establecer la fecha actual por defecto
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_cliente_modal'] = ClienteForm() # Pasa una instancia de ClienteForm al contexto para el modal
        return context

    def form_valid(self, form):
        # Asegurarse de que la fecha_prescripcion no sea manipulada por usuarios sin permiso
        if not self.request.user.is_superuser and not self.request.user.groups.filter(name__in=['Admin', 'Gerente']).exists():
            form.instance.fecha_prescripcion = date.today()
        return super().form_valid(form)


# --- Vista para Listar todas las Prescripciones ---
class PrescripcionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Prescripcion
    template_name = 'prescripciones/prescripcion_list.html'
    context_object_name = 'prescripciones'
    paginate_by = 10
    permission_required = 'prescripciones.view_prescripcion'
    raise_exception = True

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(cliente__nombre__icontains=query) |
                Q(cliente__apellido_paterno__icontains=query) |
                Q(cliente__apellido_materno__icontains=query)
            ).distinct()
            if not queryset.exists():
                messages.warning(self.request, f"No se encontraron prescripciones para la búsqueda '{query}'.")

        cliente_id = self.request.GET.get('cliente')
        if cliente_id:
            queryset = queryset.filter(cliente__id=cliente_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['titulo'] = 'Lista de Prescripciones'
        return context


# --- Vista para Ver los Detalles de una Prescripción ---
class PrescripcionDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Prescripcion
    template_name = 'prescripciones/prescripcion_detail.html'
    context_object_name = 'prescripcion'
    permission_required = 'prescripciones.view_prescripcion'
    raise_exception = True


# --- Vista para Editar una Prescripción Existente ---
class PrescripcionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, FechaPrescripcionPermisoMixin, UpdateView):
    model = Prescripcion
    form_class = PrescripcionForm
    template_name = 'prescripciones/prescripcion_form.html'
    permission_required = 'prescripciones.change_prescripcion'
    raise_exception = True
    
    def get_success_url(self):
        # CORRECCIÓN 2 de 3
        return reverse_lazy('prescripciones:prescripcion_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        if not self.request.user.is_superuser and not self.request.user.groups.filter(name__in=['Admin', 'Gerente']).exists():
            original_prescripcion = Prescripcion.objects.get(pk=self.object.pk)
            form.instance.fecha_prescripcion = original_prescripcion.fecha_prescripcion
        return super().form_valid(form)


# --- Vista para Eliminar una Prescripción ---
class PrescripcionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Prescripcion
    template_name = 'prescripciones/prescripcion_confirm_delete.html'
    # CORRECCIÓN 3 de 3
    success_url = reverse_lazy('prescripciones:prescripcion_list')
    permission_required = 'prescripciones.delete_prescripcion'
    raise_exception = True

# --- Vista AJAX para buscar clientes ---
@login_required
def buscar_clientes_ajax_prescripciones(request):
    query = request.GET.get('q', '')
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

# NUEVA VISTA AJAX para crear un cliente directamente desde la prescripción
@login_required
@permission_required('clientes.add_cliente', raise_exception=True)
@require_POST
def crear_cliente_en_prescripcion(request):
    form = ClienteForm(request.POST)
    if form.is_valid():
        cliente = form.save()
        return JsonResponse({
            'success': True,
            'message': f'Cliente {cliente.get_full_name()} creado exitosamente.',
            'cliente_id': cliente.pk,
            'cliente_text': cliente.get_full_name()
        })
    else:
        errors_dict = {field: [str(e) for e in field_errors] for field, field_errors in form.errors.items()}
        return JsonResponse({'success': False, 'errors': errors_dict}, status=400)