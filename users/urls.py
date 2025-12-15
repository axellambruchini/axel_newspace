from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Esta es la línea que faltaba y causaba el error:
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('registro/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]