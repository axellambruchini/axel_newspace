from django.shortcuts import render
from venues.models import Venue

def home(request):
    # Traemos los primeros 3 espacios activos para mostrarlos en la portada
    featured_venues = Venue.objects.filter(is_active=True)[:3]
    return render(request, 'core/home.html', {'featured_venues': featured_venues})