from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from researchers.models import Researcher


def _unique_slug_for_submission(model, value, instance_pk=None):
    base_slug = slugify(value) or "submission"
    slug = base_slug
    counter = 1

    queryset = model.objects.all()
    if instance_pk:
        queryset = queryset.exclude(pk=instance_pk)

    while queryset.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


class Submission(models.Model):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    WITHDRAWN = "withdrawn"

    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (SUBMITTED, "Submitted"),
        (WITHDRAWN, "Withdrawn"),
    ]

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    abstract = models.TextField()
    keywords = models.CharField(max_length=500, blank=True)
    submission_type = models.CharField(max_length=120, blank=True)
    category = models.ForeignKey(
        "news.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submissions",
    )
    corresponding_author = models.ForeignKey(
        "submissions.SubmissionAuthor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    cover_letter = models.TextField(blank=True)
    funding_information = models.TextField(blank=True)
    ethical_approval = models.TextField(blank=True)
    conflict_of_interest = models.TextField(blank=True)
    acknowledgements = models.TextField(blank=True)
    notes_to_editor = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Submission"
        verbose_name_plural = "Submissions"

    def clean(self):
        super().clean()
        if self.status == self.SUBMITTED and not self.pk:
            raise ValidationError({"status": "Submitted manuscripts must be saved as drafts first."})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug_for_submission(type(self), self.title, self.pk)
        else:
            self.slug = _unique_slug_for_submission(type(self), self.slug, self.pk)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class SubmissionAuthor(models.Model):
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="authors",
    )
    researcher = models.ForeignKey(
        Researcher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submission_authorships",
    )
    staff = models.ForeignKey(
        "staff.Staff",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submission_authorships",
    )
    external_name = models.CharField(max_length=200)
    author_order = models.PositiveIntegerField(default=1)
    is_primary = models.BooleanField(default=False)
    is_corresponding = models.BooleanField(default=False)
    affiliation = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    orcid = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["author_order", "id"]
        verbose_name = "Submission Author"
        verbose_name_plural = "Submission Authors"

    def clean(self):
        super().clean()
        if not self.researcher_id and not self.staff_id and not self.external_name:
            raise ValidationError({"external_name": "Author name is required."})

    def save(self, *args, **kwargs):
        if self.researcher:
            if self.researcher.staff_id and not self.staff_id:
                self.staff = self.researcher.staff
            if not self.external_name:
                self.external_name = self.researcher.display_name or self.researcher.full_name
            if not self.affiliation:
                self.affiliation = self.researcher.institution or self.researcher.department
            if not self.email and self.researcher.email:
                self.email = self.researcher.email
            if not self.orcid and self.researcher.orcid:
                self.orcid = self.researcher.orcid
        if self.staff and not self.external_name:
            self.external_name = self.staff.name
        if self.staff and not self.affiliation:
            self.affiliation = self.staff.department
        if self.staff and not self.email and getattr(self.staff.user, "email", ""):
            self.email = self.staff.user.email
        if not self.external_name:
            raise ValidationError({"external_name": "Author name is required."})
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def citation_name(self):
        if self.researcher:
            return self.researcher.display_name or self.researcher.full_name
        if self.staff:
            return self.staff.name
        return self.external_name

    def __str__(self):
        return self.citation_name


class SubmissionFile(models.Model):
    MAIN_MANUSCRIPT = "main_manuscript"
    FIGURES = "figures"
    TABLES = "tables"
    SUPPLEMENTARY = "supplementary_material"
    DATASET = "dataset"
    ETHICS = "ethics_approval"
    OTHER = "other"

    FILE_TYPE_CHOICES = [
        (MAIN_MANUSCRIPT, "Main Manuscript"),
        (FIGURES, "Figures"),
        (TABLES, "Tables"),
        (SUPPLEMENTARY, "Supplementary Material"),
        (DATASET, "Dataset"),
        (ETHICS, "Ethics Approval"),
        (OTHER, "Other"),
    ]

    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="files",
    )
    file = models.FileField(upload_to="submissions/")
    file_type = models.CharField(max_length=40, choices=FILE_TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at", "id"]
        verbose_name = "Submission File"
        verbose_name_plural = "Submission Files"

    def __str__(self):
        return f"{self.submission.title} - {self.get_file_type_display()}"

