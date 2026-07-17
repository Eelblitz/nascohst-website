from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import News, Category, Comment, PublicationAuthor


class PublicationAuthorInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        corresponding_count = 0
        primary_count = 0

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE", False):
                continue
            if form.cleaned_data.get("is_corresponding"):
                corresponding_count += 1
            if form.cleaned_data.get("is_primary"):
                primary_count += 1

        if corresponding_count > 1:
            raise ValidationError("Only one corresponding author can be marked per publication.")

        if primary_count == 0 and self.forms:
            raise ValidationError("At least one primary author should be selected.")


class PublicationAuthorInline(admin.TabularInline):
    model = PublicationAuthor
    extra = 1
    fields = (
        "display_order",
        "researcher",
        "staff",
        "external_name",
        "affiliation",
        "email",
        "orcid",
        "is_primary",
        "is_corresponding",
    )
    ordering = ("display_order", "id")
    autocomplete_fields = ("researcher", "staff")
    formset = PublicationAuthorInlineFormSet


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
    inlines = [PublicationAuthorInline]

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

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        if not obj.publication_authors.exists():
            obj.ensure_legacy_publication_author()


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
