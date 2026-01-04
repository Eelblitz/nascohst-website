from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


# --------------------------------------------------
# Image validation
# --------------------------------------------------

def validate_image_size(image):
    max_size = 2 * 1024 * 1024  # 2MB
    if image.size > max_size:
        raise ValidationError("Image size must not exceed 2MB.")


# --------------------------------------------------
# Staff Model
# --------------------------------------------------

class Staff(models.Model):
    ACADEMIC = 'academic'
    NON_ACADEMIC = 'non_academic'
    MANAGEMENT = 'management'

    CATEGORY_CHOICES = [
        (ACADEMIC, 'Academic Staff'),
        (NON_ACADEMIC, 'Non-Academic Staff'),
        (MANAGEMENT, 'Management Staff'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional system user account linked to this staff member"
    )

    name = models.CharField(max_length=200)

    photo = models.ImageField(
        upload_to='staff/',
        blank=True,
        null=True,
        validators=[validate_image_size],
        help_text="Passport photograph (max 2MB, JPG/PNG recommended)"
    )

    designation = models.CharField(max_length=150)
    department = models.CharField(max_length=150, blank=True)

    qualifications = models.TextField(
        help_text="Academic and professional qualifications"
    )

    biography = models.TextField(
        blank=True,
        help_text="Short professional biography (optional)"
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first"
    )

    is_approved = models.BooleanField(
        default=False,
        help_text="Only approved staff are visible on the public website"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name
