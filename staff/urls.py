from django.urls import path
from .views import staff_list, management_staff, staff_register

urlpatterns = [
    path('', staff_list, name='staff_list'),
    path('management/', management_staff, name='management_staff'),
    path('register/', staff_register, name='staff_register'),

]
