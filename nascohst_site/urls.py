from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home', 'about', 'contact', 'school_list', 'staff_list', 'news_list']

    def location(self, item):
        return reverse(item)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('staff/', include('staff.urls')),
    path('academics/', include('academics.urls')),
    path('news/', include('news.urls', namespace='news')),
    path('gallery/', include('gallery.urls', namespace='gallery')),
    path(
    'sitemap.xml',
    sitemap,
    {'sitemaps': {'static': StaticViewSitemap}},
    name='django.contrib.sitemaps.views.sitemap'
),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
