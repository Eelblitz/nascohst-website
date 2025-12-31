from django.urls import path
from .views import home, about, contact, admissions, robots_txt

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('admissions/', admissions, name='admissions'),
    path('robots.txt', robots_txt),
]

