from django.db import models
from academics.models import Programme
# Create your models here.




class Student(models.Model):
    LEVEL_CHOICES = [
        ('ND I', 'National Diploma 100L'),
        ('ND II', 'National Diploma 200L'),
        ('PD I', 'Professional Diploma 100L'),
        ('PD II', 'Professional Diploma 200L'),
        ('PD III', 'Professional Diploma 300L'),
        ('HND I', 'Higher National Diploma 100L'),
        ('HND II', 'Higher National Diploma 200L'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    matriculation_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Official matriculation number"
    )

    index_number = models.CharField(
        max_length=50,
        help_text="Student index number",
    )

    last_name = models.CharField(
        max_length=100,
        help_text="Student surname or family name"
    )

    other_names = models.CharField(
        max_length=150,
        blank=True,
        help_text="Student first name and other names"
    )

    programme = models.ForeignKey(
        Programme,
        on_delete=models.PROTECT,
        related_name='students'
    )

    gsm_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Student GSM/mobile number",
    )

    level = models.CharField(
        max_length=6,
        choices=LEVEL_CHOICES,
        default='ND I',
        help_text="Academic level for this student",
    )

    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        default='O',
        help_text="Gender of the student",
    )

    graduation_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Year of graduation (leave empty for current students)"
    )

    remarks = models.TextField(
        blank=True,
        null=True,
        help_text="Additional remarks about the student",
    )

    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Cumulative grade point average"
    )

    grade = models.CharField(
        max_length=50,
        blank=True,
        help_text="Final grade or classification"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'other_names']
        indexes = [
            models.Index(fields=['matriculation_number']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.matriculation_number})"

    @property
    def full_name(self):
        return " ".join(
            part for part in [self.last_name, self.other_names] if part
        )

    @property
    def school(self):
        return self.programme.school

    @property
    def programme_level(self):
        return self.programme.level

    @property
    def status(self):
        return "Alumni" if self.graduation_year else "Current"
