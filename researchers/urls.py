from django.urls import path

from .views import researcher_detail, researcher_list

app_name = "researchers"

urlpatterns = [
    path("", researcher_list, name="researcher_list"),
    path("<slug:slug>/", researcher_detail, name="researcher_detail"),
]
