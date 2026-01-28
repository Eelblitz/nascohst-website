from django.db.models import Count
from .models import Student


def student_overview():
    total = Student.objects.count()
    alumni = Student.objects.filter(graduation_year__isnull=False).count()
    current = total - alumni

    return {
        "total_students": total,
        "current_students": current,
        "alumni_students": alumni,
    }


def students_by_level():
    return (
        Student.objects
        .values("programme__level")
        .annotate(count=Count("id"))
        .order_by("programme__level")
    )


def students_by_school():
    return (
        Student.objects
        .values("programme__school__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )


def students_by_programme():
    return (
        Student.objects
        .values("programme__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )