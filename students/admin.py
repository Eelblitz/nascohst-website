"""
NOTE:
WeasyPrint-based PDF export is intentionally disabled.

Reason:
- Requires OS-level libraries (Pango/Cairo)
- Not portable across Windows dev + Linux prod yet

TODO:
- Re-enable PDF export when deployment environment is finalized
"""

from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Count, Q, Case, When
from django.db.models.functions import TruncDate

import csv
from io import TextIOWrapper

from .models import Student
from academics.models import Programme, School

# Optional PDF support (safe on Windows)
#try:
#    from weasyprint import HTML
#except Exception:
#    HTML = None


# ============================
# EXPORT ACTION (CSV)
# ============================
@admin.action(description="Export selected students to CSV")
def export_students_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Matriculation Number",
        "Index Number",
        "Full Name",
        "Programme",
        "GSM Number",
        "Level",
        "Gender",
        "Graduation Year",
        "Remarks",
    ])

    for student in queryset:
        writer.writerow([
            student.matriculation_number,
            student.index_number,
            student.full_name,
            student.programme.name,
            student.gsm_number or "",
            student.get_level_display(),
            student.get_gender_display(),
            student.graduation_year or "",
            student.remarks or "",
        ])

    return response


# ============================
# STUDENT ADMIN
# ============================
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    actions = [export_students_csv]

    list_display = (
        "matriculation_number",
        "index_number",
        "full_name",
        "programme",
        "gsm_number",
        "level",
        "gender",
        "graduation_year",
    )

    list_filter = (
        "programme",
        "level",
        "gender",
        "graduation_year",
    )

    search_fields = (
        "matriculation_number",
        "index_number",
        "full_name",
    )

    ordering = ("full_name",)

    # ============================
    # CUSTOM URLS
    # ============================
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload-csv/",
                self.admin_site.admin_view(self.upload_students_csv),
                name="students_student_upload_csv",
            ),
            path(
                "dashboard/",
                self.admin_site.admin_view(self.analytics_dashboard),
                name="students_student_dashboard",
            ),
            path(
                "download-by-department/",
                self.admin_site.admin_view(self.download_students_by_department),
                name="students_student_download_by_department",
            ),
        ]
        return custom_urls + urls

    # ============================
    # CSV UPLOAD
    # ============================
    def upload_students_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")

            if not csv_file:
                self.message_user(request, "No file uploaded.", messages.ERROR)
                return redirect(request.path)

            if not csv_file.name.endswith(".csv"):
                self.message_user(request, "Only CSV files are allowed.", messages.ERROR)
                return redirect(request.path)

            decoded_file = TextIOWrapper(csv_file.file, encoding="utf-8")
            reader = csv.DictReader(decoded_file)

            required_headers = {
                "matriculation_number",
                "index_number",
                "full_name",
                "programme",
                "graduation_year",
            }

            if not required_headers.issubset(reader.fieldnames):
                self.message_user(
                    request,
                    "Invalid CSV headers.",
                    messages.ERROR,
                )
                return redirect(request.path)

            created = 0

            with transaction.atomic():
                for row in reader:
                    try:
                        programme = Programme.objects.get(
                            name=row["programme"].strip()
                        )
                    except Programme.DoesNotExist:
                        continue

                    defaults = {
                        "index_number": row["index_number"].strip(),
                        "full_name": row["full_name"].strip(),
                        "programme": programme,
                        "graduation_year": row.get("graduation_year") or None,
                        "gsm_number": row.get("gsm_number", "").strip() or None,
                        "remarks": row.get("remarks", "").strip() or None,
                    }

                    if "level" in row and row["level"].strip():
                        defaults["level"] = row["level"].strip()

                    if "gender" in row and row["gender"].strip():
                        defaults["gender"] = row["gender"].strip()

                    _, was_created = Student.objects.get_or_create(
                        matriculation_number=row["matriculation_number"].strip(),
                        defaults=defaults,
                    )

                    if was_created:
                        created += 1

            self.message_user(
                request,
                f"Upload complete: {created} students added.",
                messages.SUCCESS,
            )
            return redirect("..")

        return render(
            request,
            "admin/students/upload_csv.html",
            {"title": "Upload Students via CSV"},
        )

    # ============================
    # DEPARTMENT EXPORT
    # ============================
    def download_students_by_department(self, request):
        school_name = request.GET.get("school_name")
        fmt = request.GET.get("format", "csv")

        schools = School.objects.order_by("name")
        queryset = Student.objects.select_related("programme", "programme__school")

        if school_name and school_name != "All Departments":
            # Find school by name (case-insensitive)
            school = schools.filter(name__iexact=school_name).first()
            if school:
                queryset = queryset.filter(programme__school=school)
                filename_school_name = school.name
            else:
                # If school not found, return empty queryset
                queryset = queryset.none()
                filename_school_name = "unknown_department"
        else:
            filename_school_name = "all_departments"

        if fmt != "csv":
            return HttpResponse(
                "Only CSV format is supported at this time.",
                status=400,
            )

        return self._export_students_csv_response(queryset, filename_school_name)

    def _export_students_csv_response(self, queryset, school_name):
        filename = f"students_{school_name.replace(' ', '_').lower()}.csv"
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow([
            "Matriculation Number",
            "Index Number",
            "Full Name",
            "Programme",
            "School",
            "GSM Number",
            "Level",
            "Gender",
            "Graduation Year",
            "Remarks",
        ])

        for student in queryset.order_by("programme__school__name", "programme__name", "full_name"):
            writer.writerow([
                student.matriculation_number,
                student.index_number,
                student.full_name,
                student.programme.name,
                student.programme.school.name,
                student.gsm_number or "",
                student.get_level_display(),
                student.get_gender_display(),
                student.graduation_year or "",
                student.remarks or "",
            ])

        return response

    # ============================
    # ANALYTICS DASHBOARD
    # ============================
    def analytics_dashboard(self, request):
        from django.db.models import Q, F, Case, When, Value, IntegerField
        from django.utils import timezone
        from datetime import timedelta
        
        total_students = Student.objects.count()
        current_students = Student.objects.filter(graduation_year__isnull=True).count()
        alumni = Student.objects.filter(graduation_year__isnull=False).count()
        
        # Calculate contact info completion
        with_contact = Student.objects.filter(gsm_number__isnull=False).exclude(gsm_number='').count()
        contact_rate = round((with_contact / total_students * 100) if total_students > 0 else 0, 1)
        
        # Recent registrations (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_registrations = Student.objects.filter(created_at__gte=thirty_days_ago).count()
        
        # Data by academic level
        by_level = (
            Student.objects
            .values("level")
            .annotate(total=Count("id"))
            .order_by("level")
        )
        
        # Data by gender
        by_gender = (
            Student.objects
            .values("gender")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        
        # Data by programme with school
        by_programme = (
            Student.objects
            .values("programme__name", "programme__school__name")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        
        # Data by school
        by_school = (
            Student.objects
            .values("programme__school__name")
            .annotate(
                total=Count("id"),
                current=Count(Case(When(graduation_year__isnull=True, then=1))),
                alumni=Count(Case(When(graduation_year__isnull=False, then=1)))
            )
            .order_by("-total")
        )

        # Status by level (distribution of current vs alumni)
        status_by_level = (
            Student.objects
            .values("level")
            .annotate(
                current=Count(Case(When(graduation_year__isnull=True, then=1))),
                alumni=Count(Case(When(graduation_year__isnull=False, then=1)))
            )
            .order_by("level")
        )

        # Gender distribution by level
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

        # Registration trend for last 30 days
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

        # Programme enrollment summary
        programme_summary = (
            Student.objects
            .values("programme__name")
            .annotate(
                total=Count("id"),
                current=Count(Case(When(graduation_year__isnull=True, then=1))),
                alumni=Count(Case(When(graduation_year__isnull=False, then=1)))
            )
            .order_by("-total")
        )

        schools = School.objects.order_by("name")

        context = {
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
            "schools": schools,
        }

        return render(
            request,
            "admin/students/student/dashboard.html",
            context,
        )
