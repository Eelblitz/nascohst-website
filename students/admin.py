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

import csv
from io import TextIOWrapper

from .models import Student
from .admin_stats import build_student_analytics_context
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
        "Last Name",
        "Other Names",
        "Programme",
        "GSM Number",
        "Level",
        "Gender",
        "Graduation Year",
        "Remarks",
        "CGPA",
        "Grade",
    ])

    for student in queryset:
        writer.writerow([
            student.matriculation_number,
            student.index_number,
            student.last_name,
            student.other_names,
            student.programme.name,
            student.gsm_number or "",
            student.get_level_display(),
            student.get_gender_display(),
            student.graduation_year or "",
            student.remarks or "",
            student.cgpa or "",
            student.grade,
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
        "last_name",
        "other_names",
        "programme",
        "gsm_number",
        "level",
        "gender",
        "graduation_year",
        "cgpa",
        "grade",
    )

    list_filter = (
        "programme",
        "level",
        "gender",
        "graduation_year",
        "grade",
    )

    search_fields = (
        "matriculation_number",
        "index_number",
        "last_name",
        "other_names",
    )

    ordering = ("last_name", "other_names")

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
                "last_name",
                "other_names",
                "programme",
                "graduation_year",
                "cgpa",
                "grade",
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

                    graduation_year = (row.get("graduation_year") or "").strip()
                    cgpa = (row.get("cgpa") or "").strip()

                    defaults = {
                        "index_number": row["index_number"].strip(),
                        "last_name": row["last_name"].strip(),
                        "other_names": (row.get("other_names") or "").strip(),
                        "programme": programme,
                        "graduation_year": graduation_year or None,
                        "gsm_number": (row.get("gsm_number") or "").strip() or None,
                        "remarks": (row.get("remarks") or "").strip() or None,
                        "cgpa": cgpa or None,
                        "grade": (row.get("grade") or "").strip(),
                    }

                    if (row.get("level") or "").strip():
                        defaults["level"] = row["level"].strip()

                    if (row.get("gender") or "").strip():
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
        programme_name = request.GET.get("programme_name")
        fmt = request.GET.get("format", "csv")

        queryset = Student.objects.select_related("programme", "programme__school")

        if programme_name and programme_name != "All Programmes":
            queryset = queryset.filter(programme__name__icontains=programme_name)
            filename_school_name = programme_name
        else:
            filename_school_name = "all_programmes"

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
            "Last Name",
            "Other Names",
            "Programme",
            "School",
            "GSM Number",
            "Level",
            "Gender",
            "Graduation Year",
            "Remarks",
            "CGPA",
            "Grade",
        ])

        for student in queryset.order_by("programme__school__name", "programme__name", "last_name", "other_names"):
            writer.writerow([
                student.matriculation_number,
                student.index_number,
                student.last_name,
                student.other_names,
                student.programme.name,
                student.programme.school.name,
                student.gsm_number or "",
                student.get_level_display(),
                student.get_gender_display(),
                student.graduation_year or "",
                student.remarks or "",
                student.cgpa or "",
                student.grade,
            ])

        return response

    # ============================
    # ANALYTICS DASHBOARD
    # ============================
    def analytics_dashboard(self, request):
        schools = School.objects.order_by("name")
        programmes = Programme.objects.order_by("name")
        context = build_student_analytics_context()
        context["schools"] = schools
        context["programmes"] = programmes

        return render(
            request,
            "admin/students/student/dashboard.html",
            context,
        )
