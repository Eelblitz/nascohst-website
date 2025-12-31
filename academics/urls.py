from django.urls import path
from .views import school_list, school_detail, programme_detail

urlpatterns = [
    path('', school_list, name='school_list'),
    path('<int:pk>/', school_detail, name='school_detail'),
    path('programme/<int:pk>/', programme_detail, name='programme_detail'),

]
