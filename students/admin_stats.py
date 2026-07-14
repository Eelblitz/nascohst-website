from datetime import timedelta

from django.db.models import Count, Q, Case, When
from django.db.models.functions import TruncDate
from django.utils import timezone

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
        .values("level")
        .annotate(count=Count("id"))
        .order_by("level")
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


def build_student_analytics_context():
    total_students = Student.objects.count()
    current_students = Student.objects.filter(graduation_year__isnull=True).count()
    alumni = Student.objects.filter(graduation_year__isnull=False).count()

    with_contact = Student.objects.filter(gsm_number__isnull=False).exclude(gsm_number="").count()
    contact_rate = round((with_contact / total_students * 100) if total_students > 0 else 0, 1)

    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_registrations = Student.objects.filter(created_at__gte=thirty_days_ago).count()

    by_level = (
        Student.objects
        .values("level")
        .annotate(total=Count("id"))
        .order_by("level")
    )

    by_gender = (
        Student.objects
        .values("gender")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    by_programme = (
        Student.objects
        .values("programme__name", "programme__school__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    by_school = (
        Student.objects
        .values("programme__school__name")
        .annotate(
            total=Count("id"),
            current=Count(Case(When(graduation_year__isnull=True, then=1))),
            alumni=Count(Case(When(graduation_year__isnull=False, then=1))),
        )
        .order_by("-total")
    )

    status_by_level = (
        Student.objects
        .values("level")
        .annotate(
            current=Count(Case(When(graduation_year__isnull=True, then=1))),
            alumni=Count(Case(When(graduation_year__isnull=False, then=1))),
        )
        .order_by("level")
    )

    gender_by_level = (
        Student.objects
        .values("level", "gender")
        .annotate(total=Count("id"))
        .order_by("level", "gender")
    )

    gender_level_series = []
    for row in by_level:
        level = row["level"]
        gender_level_series.append({
            "level": level,
            "M": sum(item["total"] for item in gender_by_level if item["level"] == level and item["gender"] == "M"),
            "F": sum(item["total"] for item in gender_by_level if item["level"] == level and item["gender"] == "F"),
            "O": sum(item["total"] for item in gender_by_level if item["level"] == level and item["gender"] == "O"),
        })

    registration_trend_qs = (
        Student.objects
        .filter(created_at__gte=thirty_days_ago)
        .annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    registration_trend = [
        {"date": row["date"].strftime("%Y-%m-%d"), "count": row["count"]}
        for row in registration_trend_qs
    ]

    missing_counts = Student.objects.aggregate(
        missing_gsm=Count("id", filter=Q(gsm_number__isnull=True) | Q(gsm_number="")),
        missing_remarks=Count("id", filter=Q(remarks__isnull=True) | Q(remarks="")),
    )

    missing_gsm_rate = round((missing_counts["missing_gsm"] / total_students * 100) if total_students else 0, 1)
    missing_remarks_rate = round((missing_counts["missing_remarks"] / total_students * 100) if total_students else 0, 1)

    programme_summary = (
        Student.objects
        .values("programme__name")
        .annotate(
            total=Count("id"),
            current=Count(Case(When(graduation_year__isnull=True, then=1))),
            alumni=Count(Case(When(graduation_year__isnull=False, then=1))),
        )
        .order_by("-total")
    )

    return {
        "title": "Student Analytics Dashboard",
        "total_students": total_students,
        "current_students": current_students,
        "alumni": alumni,
        "with_contact": with_contact,
        "contact_rate": contact_rate,
        "recent_registrations": recent_registrations,
        "missing_gsm": missing_counts["missing_gsm"],
        "missing_remarks": missing_counts["missing_remarks"],
        "missing_gsm_rate": missing_gsm_rate,
        "missing_remarks_rate": missing_remarks_rate,
        "by_level": by_level,
        "by_gender": by_gender,
        "by_programme": by_programme,
        "by_school": by_school,
        "status_by_level": status_by_level,
        "gender_level_series": gender_level_series,
        "registration_trend": registration_trend,
        "programme_summary": programme_summary,
    }
