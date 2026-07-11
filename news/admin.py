from django.contrib import admin
from .models import News, Category, Comment


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
        "status",
        "featured",
        "views",
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

    prepopulated_fields = {"slug": ("title",)}

    autocomplete_fields = ["author"]

    ordering = ("-published_at",)

    list_editable = (
        "featured",
        "status",
    )

    readonly_fields = (
        "published_at",
        "updated_at",
        "views",
    )

    fieldsets = (
        ("Article Information", {
            "fields": (
                "title",
                "slug",
                "excerpt",
                "content",
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
        ("Statistics", {
            "fields": (
                "views",
            )
        }),
        ("Timestamps", {
            "fields": (
                "published_at",
                "updated_at",
            )
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "news",
        "approved",
        "created_at",
    )

    list_filter = (
        "approved",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "body",
        "news__title",
    )

    ordering = (
        "-created_at",
    )

    list_editable = (
        "approved",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Comment", {
            "fields": (
                "news",
                "name",
                "email",
                "body",
            )
        }),
        ("Moderation", {
            "fields": (
                "approved",
            )
        }),
        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )