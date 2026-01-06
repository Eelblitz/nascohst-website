from django.urls import path
from .views import gallery_view

app_name = "gallery"

urlpatterns = [
    path('', gallery_view, name='gallery'),
]