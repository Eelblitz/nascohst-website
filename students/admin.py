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
from django.db.models import Count

import csv
from io import TextIOWrapper

from .models import Student
from academics.models import Programme

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
        "Level",
        "Gender",
        "Graduation Year",
    ])

    for student in queryset:
        writer.writerow([
            student.matriculation_number,
            student.index_number,
            student.full_name,
            student.programme.name,
            student.get_level_display(),
            student.get_gender_display(),
            student.graduation_year or "",
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
    # ANALYTICS DASHBOARD
    # ============================
    def analytics_dashboard(self, request):
        total_students = Student.objects.count()
        current_students = Student.objects.filter(graduation_year__isnull=True).count()
        alumni = Student.objects.filter(graduation_year__isnull=False).count()

        context = {
            "title": "Student Analytics Dashboard",
            "total_students": total_students,
            "current_students": current_students,
            "alumni": alumni,
            "by_programme": (
                Student.objects
                .values("programme__name")
                .annotate(total=Count("id"))
                .order_by("-total")
            ),
            "by_level": (
                Student.objects
                .values("programme__level")
                .annotate(total=Count("id"))
                .order_by("-total")
            ),
        }

        return render(
            request,
            "admin/students/student/dashboard.html",
            context,
        )
