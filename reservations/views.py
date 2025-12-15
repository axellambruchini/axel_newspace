from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Reservation, ReservationLog
from venues.models import Venue
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Reservation
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count



def create_reservation(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    
    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        event_type = request.POST.get('event_type')
        
        # 1. Verificar Disponibilidad
        # Si existe alguna reserva que se solape con las horas solicitadas
        overlap = Reservation.objects.filter(
            venue=venue,
            status__in=['PENDING', 'CONFIRMED'],
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()
        
        if overlap:
            messages.error(request, "El espacio no está disponible en ese horario.")
        else:
            Reservation.objects.create(
                client=request.user,
                venue=venue,
                start_time=start_time,
                end_time=end_time,
                event_type=event_type
            )
            messages.success(request, "Solicitud enviada exitosamente.")
            return redirect('user_dashboard') # Redirigir a panel de cliente

    return render(request, 'reservations/booking_form.html', {'venue': venue})


def is_staff_check(user):
    return user.is_staff or getattr(user, 'is_staff_member', False)

@login_required
@user_passes_test(is_staff_check)
def staff_reservation_list(request):
    """Muestra todas las reservas para que el trabajador las gestione"""
    # Filtramos por estado si viene en la URL, sino mostramos todas
    status_filter = request.GET.get('status')
    if status_filter:
        reservations = Reservation.objects.filter(status=status_filter).order_by('-created_at')
    else:
        reservations = Reservation.objects.all().order_by('-created_at')
    
    # --- LÓGICA PARA GRÁFICOS (Dashboard Analytics) ---
    
    # A. Datos para el Gráfico de Estados (Dona)
    # Esto cuenta cuántas reservas hay por cada estado: [{'status': 'CONFIRMED', 'total': 5}, ...]
    status_counts = Reservation.objects.values('status').annotate(total=Count('status'))
    
    # Preparamos listas separadas para Chart.js
    chart_labels = []
    chart_data = []
    
    # Diccionario para traducir los códigos a español bonito
    status_dict = dict(Reservation.STATUS_CHOICES)
    
    for item in status_counts:
        # Convertimos 'CONFIRMED' a 'Confirmada' usando el diccionario
        label_pretty = status_dict.get(item['status'], item['status'])
        chart_labels.append(label_pretty)
        chart_data.append(item['total'])

    # B. Datos para el Gráfico de Espacios Populares (Barras)
    venue_counts = Reservation.objects.values('venue__name').annotate(total=Count('id')).order_by('-total')[:5]
    
    venue_labels = [item['venue__name'] for item in venue_counts]
    venue_data = [item['total'] for item in venue_counts]

    context = {
        'reservations': reservations,
        'filter': status_filter,
        # Datos para JS
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'venue_labels': venue_labels,
        'venue_data': venue_data,
    }
        
    return render(request, 'reservations/staff_list.html', context)

@login_required
@user_passes_test(is_staff_check)
def manage_reservation(request, reservation_id):
    """Vista para aprobar/rechazar y dejar notas"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        staff_notes = request.POST.get('staff_notes')
        
        # Guardamos el estado anterior para saber si cambió
        old_status = reservation.status
        
        # --- LOGICA DE TRAZABILIDAD (Log) ---
        if old_status != new_status:
            ReservationLog.objects.create(
                reservation=reservation,
                changed_by=request.user,
                old_status=old_status,
                new_status=new_status,
                note=staff_notes
            )
            
            # --- NUEVO: ENVIAR CORREO DE NOTIFICACIÓN ---
            # Solo enviamos si el estado es Confirmado o Cancelado
            if new_status in ['CONFIRMED', 'CANCELLED']:
                subject = f"Actualización de tu Reserva: {reservation.venue.name}"
                message = f"""
                Hola {reservation.client.username},
                
                El estado de tu reserva para el evento '{reservation.event_type}' ha cambiado.
                
                NUEVO ESTADO: {reservation.get_status_display()}
                
                Notas del Staff:
                {staff_notes}
                
                Revisa los detalles en tu panel: http://127.0.0.1:8000/usuarios/dashboard/
                
                Atte,
                El equipo de EventosManager.
                """
                
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [reservation.client.email], # Email del usuario
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Error enviando correo: {e}")
        # LOGICA DE TRAZABILIDAD
        if reservation.status != new_status:
            # Solo creamos log si el estado cambió
            ReservationLog.objects.create(
                reservation=reservation,
                changed_by=request.user,
                old_status=reservation.status,
                new_status=new_status,
                note=staff_notes # Guardamos la nota asociada al cambio
            )
        
        # Actualizamos la trazabilidad
        reservation.status = new_status
        reservation.staff_notes = staff_notes
        reservation.save()
        
        messages.success(request, f"Reserva actualizada y notificación enviada.")
        return redirect('staff_reservation_list')
        
    return render(request, 'reservations/manage_reservation.html', {'reservation': reservation})


def venue_availability_api(request, venue_id):
    """
    Retorna un JSON con las reservas confirmadas o pendientes
    para que el calendario las muestre como 'Ocupado'.
    """
    # Filtramos reservas del lugar que NO estén canceladas ni rechazadas
    reservations = Reservation.objects.filter(
        venue_id=venue_id,
        status__in=['PENDING', 'CONFIRMED', 'COMPLETED']
    )
    
    events = []
    for res in reservations:
        # Definimos el color según el estado
        color = '#dc3545' # Rojo (Confirmado)
        title = "Ocupado"
        
        if res.status == 'PENDING':
            color = '#ffc107' # Amarillo (Pendiente)
            title = "Pendiente"

        events.append({
            'title': title,
            'start': res.start_time.isoformat(),
            'end': res.end_time.isoformat(),
            'color': color,
            'display': 'block' # Muestra bloque sólido
        })
    
    return JsonResponse(events, safe=False)