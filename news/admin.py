from django.contrib import admin
from .models import News, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "views",
        "status",
        "featured",
        "published_at",
    )

    list_filter = (
        "status",
        "featured",
        "category",
        "published_at",
    )

    search_fields = (
        "title",
        "excerpt",
        "content",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    autocomplete_fields = [
        "author",
    ]

    ordering = (
        "-published_at",
    )

    list_editable = (
        "featured",
        "status",
    )

    readonly_fields = (
        "views",
        "published_at",
        "updated_at",
    )

    fieldsets = (

        ("Article Information", {
            "fields": (
                "title",
                "slug",
                "excerpt",
                "content",
            )
        }),

        ("Media", {
            "fields": (
                "image",
                "attachment",
            )
        }),

        ("Publishing", {
            "fields": (
                "author",
                "category",
                "status",
                "featured",
            )
        }),

        ("Timestamps", {
            "fields": (
                "views",
                "published_at",
                "updated_at",
            )
        }),

    )