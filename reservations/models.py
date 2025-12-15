from django.db import models
from django.conf import settings
from venues.models import Venue

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente de Aprobación'),
        ('CONFIRMED', 'Confirmada'),
        ('COMPLETED', 'Finalizada'),
        ('CANCELLED', 'Cancelada'),
    ]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='reservations')
    
    event_type = models.CharField(max_length=100, help_text="Ej: Boda, Conferencia, Cumpleaños")
    start_time = models.DateTimeField(verbose_name="Inicio del Evento")
    end_time = models.DateTimeField(verbose_name="Fin del Evento")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Trazabilidad
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    staff_notes = models.TextField(blank=True, null=True, help_text="Notas internas del trabajador")

    def __str__(self):
        return f"{self.event_type} en {self.venue.name} - {self.start_time.date()}"

    class Meta:
        ordering = ['-created_at']
        

class ReservationLog(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='logs')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Cambio de {self.old_status} a {self.new_status} - {self.timestamp}"