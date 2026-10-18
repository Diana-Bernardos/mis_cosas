import calendar
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import RegistroForm, TareaForm
from .models import Tarea


MESES = (
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
)


def _calendario_contexto(request, fecha_referencia=None):
    hoy = timezone.localdate()
    if fecha_referencia is None:
        try:
            fecha_referencia = date(
                int(request.GET.get('year', hoy.year)),
                int(request.GET.get('month', hoy.month)),
                1,
            )
        except (TypeError, ValueError):
            fecha_referencia = date(hoy.year, hoy.month, 1)

    tareas = list(
        Tarea.objects.filter(usuario=request.user).order_by(
            'fecha_vencimiento', 'nombre'
        )
    )
    tareas_por_fecha = {}
    for tarea in tareas:
        tareas_por_fecha.setdefault(tarea.fecha_vencimiento, []).append(tarea)

    calendario = calendar.Calendar(firstweekday=0)
    semanas = [
        [
            {
                'fecha': dia,
                'en_mes': dia.month == fecha_referencia.month,
                'tareas': tareas_por_fecha.get(dia, []),
            }
            for dia in semana
        ]
        for semana in calendario.monthdatescalendar(
            fecha_referencia.year, fecha_referencia.month
        )
    ]

    mes_siguiente = (
        1 if fecha_referencia.month == 12 else fecha_referencia.month + 1
    )
    ano_siguiente = fecha_referencia.year + (fecha_referencia.month == 12)
    mes_anterior = (
        12 if fecha_referencia.month == 1 else fecha_referencia.month - 1
    )
    ano_anterior = fecha_referencia.year - (fecha_referencia.month == 1)

    return {
        'tareas': tareas,
        'semanas': semanas,
        'nombre_mes': f'{MESES[fecha_referencia.month - 1]} {fecha_referencia.year}',
        'mes_anterior': mes_anterior,
        'ano_anterior': ano_anterior,
        'mes_siguiente': mes_siguiente,
        'ano_siguiente': ano_siguiente,
        'dias_semana': ('Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'),
    }


def registro(request):
    if request.user.is_authenticated:
        return redirect('mis_tareas')

    form = RegistroForm(
        request.POST if request.method == 'POST' else None
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cuenta creada. Ya puedes iniciar sesión.')
        return redirect('login')
    return render(request, 'registro.html', {'form': form})


@login_required
def mis_tareas_v(request):
    context = _calendario_contexto(request)
    context['tareas_pendientes'] = [
        tarea for tarea in context['tareas'] if not tarea.completada
    ]
    return render(request, 'main.html', context)


@login_required
def crear_tarea(request):
    fecha_inicial = timezone.localdate()
    fecha_solicitada = request.GET.get('fecha')
    if fecha_solicitada:
        try:
            fecha_inicial = date.fromisoformat(fecha_solicitada)
        except ValueError:
            pass

    form = TareaForm(
        request.POST if request.method == 'POST' else None,
        initial={'fecha_vencimiento': fecha_inicial},
    )
    if request.method == 'POST' and form.is_valid():
        tarea = form.save(commit=False)
        tarea.usuario = request.user
        tarea.save()
        messages.success(request, 'Tarea añadida.')
        return redirect(
            f"{reverse('mis_tareas')}?year={tarea.fecha_vencimiento.year}"
            f"&month={tarea.fecha_vencimiento.month}"
        )

    return render(
        request,
        'tarea_form.html',
        {'form': form, 'titulo': 'Añadir una tarea'},
    )


@login_required
def editar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, pk=tarea_id, usuario=request.user)
    form = TareaForm(
        request.POST if request.method == 'POST' else None,
        instance=tarea,
    )

    if request.method == 'POST' and form.is_valid():
        tarea = form.save()
        messages.success(request, 'Tarea modificada.')
        return redirect(
            f"{reverse('mis_tareas')}?year={tarea.fecha_vencimiento.year}"
            f"&month={tarea.fecha_vencimiento.month}"
        )

    return render(
        request,
        'tarea_form.html',
        {'form': form, 'titulo': 'Modificar tarea'},
    )


@login_required
def eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, pk=tarea_id, usuario=request.user)
    if request.method == 'POST':
        tarea.delete()
        messages.success(request, 'Tarea eliminada.')
        return redirect('mis_tareas')
    return render(request, 'confirmar_eliminacion.html', {'tarea': tarea})
