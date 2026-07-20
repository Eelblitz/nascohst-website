from django.urls import path

from .views import (
    submission_create,
    submission_dashboard,
    submission_detail,
    submission_edit,
    submission_success,
)

app_name = "submissions"

urlpatterns = [
    path("submit/", submission_create, name="submission_create"),
    path("submissions/", submission_dashboard, name="submission_dashboard"),
    path("submissions/<int:pk>/", submission_detail, name="submission_detail"),
    path("submissions/<int:pk>/edit/", submission_edit, name="submission_edit"),
    path("submissions/success/", submission_success, name="submission_success"),
]

