from django.contrib import admin
from django.utils.html import format_html

from .models import AboutPage
from .models import SitePopup

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


@admin.register(SitePopup)
class SitePopupAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_active",
        "display_order",
        "start_date",
        "end_date",
        "image_preview",
        "updated_at",
    )
    list_filter = ("is_active", "start_date", "end_date", "created_at")
    search_fields = ("title", "message", "button_text", "button_url")
    date_hierarchy = "created_at"
    ordering = ("display_order", "-created_at")

    fieldsets = (
        ("Content", {"fields": ("title", "message", "image", "image_preview")}),
        ("Button", {"fields": ("button_text", "button_url")}),
        ("Visibility", {"fields": ("is_active", "start_date", "end_date", "display_order")}),
    )
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 80px; max-width: 120px; object-fit: cover; border-radius: 8px;" />',
                obj.image.url,
            )
        return "No image"

    image_preview.short_description = "Preview"
