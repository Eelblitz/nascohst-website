from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils.timezone import now

from news.models import News
from academics.models import Programme, School


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "home",
            "about",
            "contact",
            "school_list",
            "staff_list",
            "news_list",
        ]

    def location(self, item):
        return reverse(item)


class NewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return News.objects.filter(published_at__isnull=False, published_at__lte=now()).order_by('-published_at')

    def lastmod(self, obj):
        return obj.published_at

    def location(self, obj):
        return reverse('news:news_detail', args=[obj.pk])


class ProgrammeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Programme.objects.select_related('school').all()

    def location(self, obj):
        return reverse('programme_detail', args=[obj.pk])


class SchoolSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return School.objects.all()

    def location(self, obj):
        return reverse('school_detail', args=[obj.pk])


urlpatterns = [
    path("manage/portal/", admin.site.urls),

    path("", include("core.urls")),
    path("staff/", include("staff.urls")),
    path("academics/", include("academics.urls")),
    path("news/", include("news.urls")),
    path("gallery/", include("gallery.urls")),

    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": {
                "static": StaticViewSitemap,
                "news": NewsSitemap,
                "programme": ProgrammeSitemap,
                "school": SchoolSitemap,
            }
        },
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)