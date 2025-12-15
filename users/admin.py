from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Registramos el usuario personalizado para que aparezca en el panel de admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Agregamos los campos nuevos a los fieldsets del admin
    fieldsets = UserAdmin.fieldsets + (
        ('Información Extra', {'fields': ('is_client', 'is_staff_member', 'phone')}),
    )