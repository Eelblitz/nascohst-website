from django import forms
from django.core.exceptions import ValidationError

from .models import Submission, SubmissionAuthor, SubmissionFile


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = [
            "title",
            "slug",
            "abstract",
            "keywords",
            "submission_type",
            "category",
            "status",
            "cover_letter",
            "funding_information",
            "ethical_approval",
            "conflict_of_interest",
            "acknowledgements",
            "notes_to_editor",
        ]

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        title = cleaned_data.get("title")
        abstract = cleaned_data.get("abstract")

        if status == Submission.SUBMITTED:
            if not title:
                self.add_error("title", "Title is required for submitted manuscripts.")
            if not abstract:
                self.add_error("abstract", "Abstract is required for submitted manuscripts.")

        return cleaned_data


class SubmissionAuthorForm(forms.ModelForm):
    class Meta:
        model = SubmissionAuthor
        fields = [
            "researcher",
            "staff",
            "external_name",
            "author_order",
            "is_primary",
            "is_corresponding",
            "affiliation",
            "email",
            "orcid",
        ]

    def clean(self):
        cleaned_data = super().clean()
        researcher = cleaned_data.get("researcher")
        staff = cleaned_data.get("staff")
        external_name = cleaned_data.get("external_name")

        if not researcher and not staff and not external_name:
            raise ValidationError("Author name is required.")

        return cleaned_data


class SubmissionFileForm(forms.ModelForm):
    class Meta:
        model = SubmissionFile
        fields = [
            "file",
            "file_type",
            "description",
        ]

