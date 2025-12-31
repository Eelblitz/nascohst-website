from django.urls import path
from .views import gallery_list

urlpatterns = [
    path('', gallery_list, name='gallery'),
]
