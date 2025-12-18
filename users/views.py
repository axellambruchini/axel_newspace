from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from reservations.models import Reservation
from django.contrib import messages
from .forms import CustomUserCreationForm, UserUpdateForm

@login_required
def user_dashboard(request):
    # Obtenemos las reservas del usuario actual ordenadas por fecha de creación
    my_reservations = Reservation.objects.filter(client=request.user).order_by('-created_at')
    
    context = {
        'reservations': my_reservations
    }
    return render(request, 'users/dashboard.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada exitosamente. ¡Ahora puedes iniciar sesión!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Cargamos el form con los datos que envió el usuario (POST)
        # Y le decimos que actualice al usuario actual (instance=request.user)
        form = UserUpdateForm(request.POST, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado correctamente!')
            return redirect('user_dashboard') # Volvemos al panel
            
    else:
        # Si es GET, mostramos el form lleno con los datos actuales
        form = UserUpdateForm(instance=request.user)

    return render(request, 'users/edit_profile.html', {'form': form})