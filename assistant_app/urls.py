from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    # Keep the trailing slash consistent with the Unity and voice-client URLs.
    path('command/', views.command_view, name='command'),
]
