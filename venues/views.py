from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Venue
from external_apis.services import get_weather_forecast

def venue_list(request):
    # 1. Obtenemos todos los activos base
    venues = Venue.objects.filter(is_active=True)
    
    # 2. Capturamos los parámetros de la URL (?q=Boda)
    search_query = request.GET.get('q')
    
    # 3. Filtramos si hay búsqueda
    if search_query:
        venues = venues.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(amenities__name__icontains=search_query)
        ).distinct() # distinct() evita duplicados si coincide en nombre y amenity
        
    context = {
        'venues': venues,
        'search_query': search_query # Para mantener el texto en la cajita
    }
    return render(request, 'venues/venue_list.html', context)

def venue_detail(request, venue_id):
    # Detalles, especificaciones, fotos y mapa
    venue = get_object_or_404(Venue, pk=venue_id)
    # Obtenemos las fotos
    photos = venue.images.all()
    weather_info = get_weather_forecast(venue.latitude, venue.longitude, None)
    
    context = {
        'venue': venue,
        'photos': photos,
        'GOOGLE_MAPS_API_KEY': 'TU_API_KEY_AQUI', # Necesario para el mapa en el frontend
        'weather_info': weather_info,
    }
    return render(request, 'venues/venue_detail.html', context)