from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.html import format_html

from .models import Submission, SubmissionAuthor, SubmissionFile


class SubmissionAuthorInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        primary_count = 0
        corresponding_count = 0
        author_count = 0

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE", False):
                continue
            if form.cleaned_data:
                author_count += 1
            if form.cleaned_data.get("is_primary"):
                primary_count += 1
            if form.cleaned_data.get("is_corresponding"):
                corresponding_count += 1

        if author_count == 0:
            raise ValidationError("At least one submission author is required.")

        if primary_count > 1:
            raise ValidationError("Only one primary author can be marked per submission.")

        if corresponding_count > 1:
            raise ValidationError("Only one corresponding author can be marked per submission.")


class SubmissionAuthorInline(admin.TabularInline):
    model = SubmissionAuthor
    extra = 1
    fields = (
        "author_order",
        "researcher",
        "staff",
        "external_name",
        "affiliation",
        "email",
        "orcid",
        "is_primary",
        "is_corresponding",
    )
    ordering = ("author_order", "id")
    autocomplete_fields = ("researcher", "staff")
    formset = SubmissionAuthorInlineFormSet


class SubmissionFileInline(admin.TabularInline):
    model = SubmissionFile
    extra = 1
    fields = ("file_type", "file", "description", "uploaded_at")
    readonly_fields = ("uploaded_at",)
    ordering = ("-uploaded_at", "id")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status_badge",
        "status",
        "category",
        "submitted_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "category",
        "submitted_at",
        "updated_at",
    )
    search_fields = (
        "title",
        "slug",
        "abstract",
        "keywords",
        "submission_type",
        "cover_letter",
        "notes_to_editor",
    )
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-submitted_at",)
    readonly_fields = ("submitted_at", "updated_at")
    inlines = [SubmissionAuthorInline, SubmissionFileInline]

    fieldsets = (
        ("Submission Information", {
            "fields": (
                "title",
                "slug",
                "abstract",
                "keywords",
                "submission_type",
                "category",
                "status",
            )
        }),
        ("Editorial Notes", {
            "fields": (
                "cover_letter",
                "funding_information",
                "ethical_approval",
                "conflict_of_interest",
                "acknowledgements",
                "notes_to_editor",
            )
        }),
        ("Timestamps", {
            "fields": (
                "submitted_at",
                "updated_at",
            )
        }),
    )

    def status_badge(self, obj):
        colors = {
            Submission.DRAFT: "#6b7280",
            Submission.SUBMITTED: "#2563eb",
            Submission.WITHDRAWN: "#dc2626",
        }
        label = obj.get_status_display()
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="display:inline-block;padding:4px 10px;border-radius:9999px;background:{};color:#fff;font-weight:600;">{}</span>',
            color,
            label,
        )

    status_badge.short_description = "Status"
