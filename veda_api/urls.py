from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [path("health", views.health, name="health"), path("api/v1/command", views.command, name="command")]

urlpatterns += [
    # Add the view for the web UI
    path("", views.index, name="index"),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
