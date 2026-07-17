from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count

from news.models import PublicationAuthor

from .models import Researcher


@admin.register(Researcher)
class ResearcherAdmin(admin.ModelAdmin):
    list_display = (
        "admin_photo_preview",
        "display_name",
        "institution",
        "department",
        "publication_count",
        "is_internal",
        "is_verified",
        "is_active",
        "display_order",
    )
    list_filter = (
        "is_internal",
        "is_verified",
        "is_active",
        "country",
        "institution",
        "department",
    )
    search_fields = (
        "display_name",
        "first_name",
        "last_name",
        "institution",
        "department",
        "email",
        "orcid",
    )
    readonly_fields = ("joined_at", "updated_at", "photo_preview")
    fieldsets = (
        ("Identity", {
            "fields": (
                "user",
                "staff",
                "title",
                "first_name",
                "middle_name",
                "last_name",
                "display_name",
                "slug",
                "photo",
                "photo_preview",
            ),
        }),
        ("Profile", {
            "fields": (
                "biography",
                "email",
                "phone",
                "department",
                "institution",
                "country",
                "city",
                "highest_qualification",
                "specialization",
                "research_interests",
            ),
        }),
        ("Links", {
            "fields": (
                "orcid",
                "google_scholar",
                "researchgate",
                "linkedin",
                "website",
            ),
        }),
        ("Status", {
            "fields": (
                "is_internal",
                "is_verified",
                "is_active",
                "display_order",
                "joined_at",
                "updated_at",
            ),
        }),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height:120px; max-width:120px; object-fit:cover;" />',
                obj.photo.url,
            )
        return "-"

    photo_preview.short_description = "Photo Preview"

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_publication_count=Count("publication_authorships", distinct=True))

    def publication_count(self, obj):
        return getattr(obj, "_publication_count", 0)

    publication_count.short_description = "Publications"

    def admin_photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:42px; height:42px; border-radius:9999px; object-fit:cover;" />',
                obj.photo.url,
            )
        return format_html('<div style="width:42px;height:42px;border-radius:9999px;background:#e5e7eb;"></div>')

    admin_photo_preview.short_description = "Photo"


@admin.register(PublicationAuthor)
class PublicationAuthorAdmin(admin.ModelAdmin):
    list_display = ("publication", "author_identity", "affiliation", "is_primary", "is_corresponding", "display_order")
    search_fields = ("publication__title", "external_name", "staff__name", "researcher__display_name")
    autocomplete_fields = ("publication", "staff", "researcher")

    def author_identity(self, obj):
        return obj.citation_name

    author_identity.short_description = "Author"
