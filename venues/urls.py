from django.urls import path
from . import views

urlpatterns = [
    path('', views.venue_list, name='venue_list'),
    path('<int:venue_id>/', views.venue_detail, name='venue_detail'),
]