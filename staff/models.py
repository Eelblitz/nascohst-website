from django.db import models
from django.conf import settings

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
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='staff/', blank=True)
    designation = models.CharField(max_length=150)
    department = models.CharField(max_length=150, blank=True)
    qualifications = models.TextField()
    biography = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    display_order = models.PositiveIntegerField(default=0)

    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
