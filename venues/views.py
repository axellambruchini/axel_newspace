from django.contrib import messages
from django.contrib import messages as flash_messages
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q
from .models import Venue, VenueImage, Amenity
from external_apis.services import get_weather_forecast
from .forms import VenueForm, AmenityForm
from django.contrib.auth.decorators import login_required, user_passes_test
import requests
from django.conf import settings

def is_staff_check(user):
    return user.is_staff or getattr(user, 'is_staff_member', False)

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
    weather_data = None
    
    # Solo buscamos el clima si el lugar tiene coordenadas
    if venue.latitude and venue.longitude:
        # 1. Tu API KEY (Pégala aquí entre comillas)
        api_key = "9b3929a0076430546bfc70e89ffd938c" 
        
        # 2. Construimos la URL de la petición
        # units=metric: Para que nos de Celsius
        # lang=es: Para que la descripción sea en español
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={venue.latitude}&lon={venue.longitude}&appid={api_key}&units=metric&lang=es"
        
        try:
            # 3. Hacemos la petición a internet
            response = requests.get(url, timeout=5)
            
            # 4. Si la respuesta es exitosa (Código 200)
            if response.status_code == 200:
                data = response.json() # Convertimos el JSON a diccionario Python
                
                # 5. Empaquetamos solo lo que nos sirve
                weather_data = {
                    'temp': round(data['main']['temp']), # Temperatura redondeada
                    'description': data['weather'][0]['description'].capitalize(), # "Cielo claro"
                    'icon': data['weather'][0]['icon'], # Código del icono (ej: 01d)
                    'humidity': data['main']['humidity'],
                    'wind': data['wind']['speed']
                }
            else:
                print("Error en API Clima:", response.status_code)
                
        except Exception as e:
            # Si se cae internet o la API, no rompemos la página, solo imprimimos el error
            print(f"Error conectando al servicio de clima: {e}")
    context = {
        'venue': venue,
        'photos': photos,
        'GOOGLE_MAPS_API_KEY': 'TU_API_KEY_AQUI', # Necesario para el mapa en el frontend
        'weather_info': weather_info,
        'weather_data': weather_data,
    }
    return render(request, 'venues/venue_detail.html', context)


# 1. LISTAR (Panel de control de espacios)
@login_required
@user_passes_test(is_staff_check)
def staff_venue_list(request):
    venues = Venue.objects.all().order_by('-id')
    return render(request, 'venues/staff_venue_list.html', {'venues': venues})

# 2. CREAR
@login_required
@user_passes_test(is_staff_check)
def create_venue(request):
    if request.method == 'POST':
        # --- AGREGA ESTAS 3 LINEAS PARA DEPURAR ---
        print("--- DEPURACION ---")
        print("POST contiene:", request.POST)
        print("FILES contiene:", request.FILES)
        # request.FILES es obligatorio para subir fotos/modelos
        form = VenueForm(request.POST, request.FILES) 
        if form.is_valid():
            venue = form.save()
            # --- LÓGICA PARA GUARDAR FOTOS ---
            # Recorremos la lista de archivos subidos en el campo 'photos'
            images = request.FILES.getlist('photos')
            for image in images:
                VenueImage.objects.create(venue=venue, image=image)

            messages.success(request, f'Espacio "{venue.name}" creado correctamente.')
            return redirect('staff_venue_list')
        
    else:
        form = VenueForm()
    return render(request, 'venues/venue_form.html', {'form': form, 'title': 'Crear Nuevo Espacio'})

# 3. EDITAR
@login_required
@user_passes_test(is_staff_check)
def edit_venue(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)
    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES, instance=venue)
        if form.is_valid():
            form.save()
            # --- LÓGICA PARA GUARDAR FOTOS NUEVAS ---
            # Las fotos nuevas se AGREGAN a las existentes
            images = request.FILES.getlist('photos')
            for image in images:
                VenueImage.objects.create(venue=venue, image=image)
            messages.success(request, 'Cambios guardados exitosamente.')
            return redirect('staff_venue_list')
    else:
        form = VenueForm(instance=venue)
    return render(request, 'venues/venue_form.html', {'form': form, 'title': f'Editar {venue.name}'})

# 4. BORRAR
@login_required
@user_passes_test(is_staff_check)
def delete_venue(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)
    if request.method == 'POST':
        venue.delete()
        messages.success(request, 'Espacio eliminado.')
        return redirect('staff_venue_list')
    return render(request, 'venues/venue_confirm_delete.html', {'venue': venue})

# --- GESTIÓN DE INSTALACIONES (AMENITIES) ---

# 1. LISTAR
@login_required
@user_passes_test(is_staff_check)
def staff_amenity_list(request):
    amenities = Amenity.objects.all().order_by('name')
    return render(request, 'venues/amenity_list.html', {'amenities': amenities})

# 2. CREAR
@login_required
@user_passes_test(is_staff_check)
def create_amenity(request):
    if request.method == 'POST':
        form = AmenityForm(request.POST)
        if form.is_valid():
            form.save()
            flash_messages.success(request, 'Instalación agregada correctamente.')
            return redirect('staff_amenity_list')
    else:
        form = AmenityForm()
    return render(request, 'venues/amenity_form.html', {'form': form, 'title': 'Nueva Instalación'})

# 3. EDITAR
@login_required
@user_passes_test(is_staff_check)
def edit_amenity(request, pk):
    amenity = get_object_or_404(Amenity, pk=pk)
    if request.method == 'POST':
        form = AmenityForm(request.POST, instance=amenity)
        if form.is_valid():
            form.save()
            flash_messages.success(request, 'Instalación actualizada.')
            return redirect('staff_amenity_list')
    else:
        form = AmenityForm(instance=amenity)
    return render(request, 'venues/amenity_form.html', {'form': form, 'title': 'Editar Instalación'})

# 4. BORRAR
@login_required
@user_passes_test(is_staff_check)
def delete_amenity(request, pk):
    amenity = get_object_or_404(Amenity, pk=pk)
    if request.method == 'POST':
        amenity.delete()
        flash_messages.success(request, 'Instalación eliminada.')
        return redirect('staff_amenity_list')
    return render(request, 'venues/amenity_confirm_delete.html', {'amenity': amenity})