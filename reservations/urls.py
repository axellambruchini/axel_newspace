from django.urls import path
from . import views

urlpatterns = [
    path('crear/<int:venue_id>/', views.create_reservation, name='create_reservation'),
    path('gestion/', views.staff_reservation_list, name='staff_reservation_list'),
    path('gestion/<int:reservation_id>/', views.manage_reservation, name='manage_reservation'),
    path('api/availability/<int:venue_id>/', views.venue_availability_api, name='venue_availability_api'),
]