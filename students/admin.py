from django.contrib import admin, messages
from django.shortcuts import render, redirect
from io import TextIOWrapper
import csv

from .models import Student
from academics.models import Programme


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'matriculation_number',
        'full_name',
        'school',
        'programme',
        'level',
        'graduation_year',
    )

    list_filter = (
        'programme__school',
        'programme__level',
        'programme',
        'graduation_year',
    )

    search_fields = (
        'matriculation_number',
        'full_name',
    )

    ordering = ('full_name',)

    actions = ['upload_students_csv']

    # 🔒 Lock alumni records
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.graduation_year:
            return [field.name for field in obj._meta.fields]
        return []

    # 📥 Bulk upload
    def upload_students_csv(self, request, queryset):
        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")
            if not csv_file:
                self.message_user(request, "No file uploaded.", messages.ERROR)
                return redirect(request.path)

            decoded = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.DictReader(decoded)

            created, skipped = 0, 0

            for row in reader:
                try:
                    programme = Programme.objects.get(name=row['programme'])
                    Student.objects.get_or_create(
                        matriculation_number=row['matriculation_number'],
                        defaults={
                            'full_name': row['full_name'],
                            'programme': programme,
                            'graduation_year': row.get('graduation_year') or None
                        }
                    )
                    created += 1
                except Programme.DoesNotExist:
                    skipped += 1

            self.message_user(
                request,
                f"Upload complete: {created} added, {skipped} skipped.",
                messages.SUCCESS
            )
            return redirect(request.path)

        return render(request, "admin/students/upload_csv.html")

    upload_students_csv.short_description = "Upload students via CSV"
