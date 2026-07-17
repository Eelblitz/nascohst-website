from django.conf import settings
from django.db import models
from django.utils.text import slugify

from staff.models import Staff


def _unique_slug_for_model(model, value, instance_pk=None):
    base_slug = slugify(value) or "researcher"
    slug = base_slug
    counter = 1

    queryset = model.objects.all()
    if instance_pk:
        queryset = queryset.exclude(pk=instance_pk)

    while queryset.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


class Researcher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="researcher_profile",
    )
    staff = models.OneToOneField(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="researcher_profile",
    )
    title = models.CharField(max_length=50, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    display_name = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to="researchers/", blank=True, null=True)
    biography = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    department = models.CharField(max_length=150, blank=True)
    institution = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    highest_qualification = models.CharField(max_length=150, blank=True)
    specialization = models.CharField(max_length=200, blank=True)
    research_interests = models.TextField(blank=True)
    orcid = models.CharField(max_length=255, blank=True)
    google_scholar = models.URLField(blank=True)
    researchgate = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    website = models.URLField(blank=True)
    is_internal = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "display_name", "last_name", "first_name", "id"]
        verbose_name = "Researcher"
        verbose_name_plural = "Researchers"

    def sync_from_staff(self):
        if not self.staff:
            return

        staff = self.staff
        if not self.display_name:
            self.display_name = staff.name
        if not self.department:
            self.department = staff.department
        if not self.biography:
            self.biography = staff.biography
        if not self.photo and staff.photo:
            self.photo = staff.photo
        if not self.title and staff.designation:
            self.title = staff.designation
        if not self.email and getattr(staff.user, "email", ""):
            self.email = staff.user.email

        parts = staff.name.split()
        if not self.first_name and parts:
            self.first_name = parts[0]
        if not self.last_name and len(parts) > 1:
            self.last_name = parts[-1]

        if not self.is_internal:
            self.is_internal = True

    def save(self, *args, **kwargs):
        if self.staff_id:
            self.sync_from_staff()

        if not self.display_name:
            self.display_name = " ".join(part for part in [self.title, self.first_name, self.middle_name, self.last_name] if part).strip()

        if not self.display_name:
            self.display_name = self.email.split("@")[0] if self.email else "Researcher"

        if not self.slug:
            self.slug = _unique_slug_for_model(type(self), self.display_name, self.pk)
        else:
            self.slug = _unique_slug_for_model(type(self), self.slug, self.pk)

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        parts = [self.title, self.first_name, self.middle_name, self.last_name]
        full_name = " ".join(part for part in parts if part).strip()
        return full_name or self.display_name or "Researcher"

    def __str__(self):
        return self.display_name or self.full_name
