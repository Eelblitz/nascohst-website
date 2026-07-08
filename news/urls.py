from django.urls import path
from .views import news_list, news_detail, news_detail_slug

app_name = "news"

urlpatterns = [
    path("", news_list, name="news_list"),

    # Existing URL (keep for backward compatibility)
    path("<int:pk>/", news_detail, name="news_detail"),

    # New SEO-friendly URL
    path("<slug:slug>/", news_detail_slug, name="news_detail_slug"),
]