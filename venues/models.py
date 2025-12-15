from django.db import models

class Amenity(models.Model):
    """Cosas con las que cuenta el espacio (Wifi, Proyector, Cocina, etc.)"""
    name = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=50, help_text="Clase CSS para icono (ej: fa-wifi)")

    def __str__(self):
        return self.name

class Venue(models.Model):
    """El lugar o salón reservable"""
    name = models.CharField(max_length=200, verbose_name="Nombre del Espacio")
    description = models.TextField(verbose_name="Descripción")
    capacity = models.PositiveIntegerField(verbose_name="Capacidad de personas")
    size_sqm = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Tamaño (m2)")
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    # Campo nuevo para el archivo 3D
    ar_model = models.FileField(
        upload_to='venues/3d/', 
        blank=True, 
        null=True, 
        verbose_name="Modelo 3D (.glb)",
        help_text="Sube aquí tu archivo .glb para Realidad Aumentada"
    )
    
    # Geolocalización para el Mapa
    latitude = models.FloatField(help_text="Latitud para el mapa")
    longitude = models.FloatField(help_text="Longitud para el mapa")
    
    # Relación Muchos a Muchos con las comodidades
    amenities = models.ManyToManyField(Amenity, blank=True, verbose_name="Instalaciones/Comodidades")
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class VenueImage(models.Model):
    """Fotos de los lugares (Galería)"""
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='venues/')
    is_cover = models.BooleanField(default=False, help_text="Es la foto principal?")

    def __str__(self):
        return f"Imagen de {self.venue.name}"