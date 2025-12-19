from django.urls import path
from . import views

urlpatterns = [
    path('', views.venue_list, name='venue_list'),
    path('<int:venue_id>/', views.venue_detail, name='venue_detail'),
    path('gestion/', views.staff_venue_list, name='staff_venue_list'),
    path('gestion/crear/', views.create_venue, name='create_venue'),
    path('gestion/editar/<int:venue_id>/', views.edit_venue, name='edit_venue'),
    path('gestion/borrar/<int:venue_id>/', views.delete_venue, name='delete_venue'),
    path('gestion/instalaciones/', views.staff_amenity_list, name='staff_amenity_list'),
    path('gestion/instalaciones/crear/', views.create_amenity, name='create_amenity'),
    path('gestion/instalaciones/editar/<int:pk>/', views.edit_amenity, name='edit_amenity'),
    path('gestion/instalaciones/borrar/<int:pk>/', views.delete_amenity, name='delete_amenity'),
]