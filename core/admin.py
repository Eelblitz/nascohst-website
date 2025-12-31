from django.contrib import admin
from .models import AboutPage

admin.site.site_header = "Nasarawa State College of Health Science and Technology"
admin.site.site_title = "NasCOHST Admin Portal"
admin.site.index_title = "College Website Management"

@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    fieldsets = (
        ("History", {"fields": ("history",)}),
        ("Vision", {"fields": ("vision",)}),
        ("Mission", {"fields": ("mission",)}),
    )
