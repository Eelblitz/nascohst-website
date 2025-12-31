from django.contrib import admin
from .models import Staff

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'category', 'is_approved')
    list_filter = ('category', 'is_approved')
    search_fields = ('name', 'designation')
    ordering = ('is_approved', 'display_order')
    actions = ['approve_staff']

    def approve_staff(self, request, queryset):
        queryset.update(is_approved=True)

    approve_staff.short_description = "Approve selected staff"
