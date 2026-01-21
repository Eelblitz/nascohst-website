from django.db import models
from academics.models import Programme
# Create your models here.




class Student(models.Model):
    matriculation_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Official matriculation number"
    )

    full_name = models.CharField(
        max_length=200,
        help_text="Student full name as it appears on records"
    )

    programme = models.ForeignKey(
        Programme,
        on_delete=models.PROTECT,
        related_name='students'
    )

    graduation_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Year of graduation (leave empty for current students)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['matriculation_number']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.matriculation_number})"

    @property
    def school(self):
        return self.programme.school

    @property
    def level(self):
        return self.programme.level

    @property
    def status(self):
        return "Alumni" if self.graduation_year else "Current"