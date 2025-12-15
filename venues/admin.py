from django.contrib import admin
from .models import Venue, Amenity, VenueImage

class VenueImageInline(admin.TabularInline):
    model = VenueImage
    extra = 1

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'price_per_hour', 'is_active')
    search_fields = ('name',)
    # Esto permite agregar fotos directamente dentro de la pantalla del Venue
    inlines = [VenueImageInline]

admin.site.register(Amenity)