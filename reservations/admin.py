from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('client', 'venue', 'start_time', 'status')
    list_filter = ('status', 'start_time', 'venue')
    search_fields = ('client__username', 'venue__name')