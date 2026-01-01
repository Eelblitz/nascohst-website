from django.urls import path
from .views import home, about, contact, admissions, robots_txt, privacy_policy, terms_of_use, admissions_disclaimer

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('admissions/', admissions, name='admissions'),
    path('robots.txt', robots_txt),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('terms-of-use/', terms_of_use, name='terms_of_use'),
    path('admissions-disclaimer/', admissions_disclaimer, name='admissions_disclaimer'),

]

