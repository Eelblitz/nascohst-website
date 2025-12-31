from django.db import models
from staff.models import Staff


class School(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(
        help_text="Brief description of the school and its academic focus"
    )

    dean = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'category': Staff.ACADEMIC},
        related_name='dean_of'
    )

    def __str__(self):
        return self.name


class Programme(models.Model):
    LEVEL_CHOICES = [
        ('PD', 'Professional Diploma'),
        ('ND', 'National Diploma'),
        ('HND', 'Higher National Diploma'),
    ]

    name = models.CharField(max_length=200)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='programmes'
    )
    level = models.CharField(
        max_length=5,
        choices=LEVEL_CHOICES
    )

    description = models.TextField(
        blank=True,
        help_text="Brief overview of the programme"
    )

    duration = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. 2 Years, 3 Years"
    )

    entry_requirements = models.TextField(
        blank=True,
        help_text="O'Level subjects, JAMB requirements, or HND conditions"
    )

    certification = models.CharField(
        max_length=200,
        blank=True,
        help_text="Certificate awarded upon successful completion"
    )

    career_prospects = models.TextField(
        blank=True,
        help_text="Possible career paths for graduates"
    )

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"
