from django.contrib import admin
from .models import School, Programme


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'dean')
    search_fields = ('name',)


from django.contrib import admin
from .models import Programme

@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'level')
    list_filter = ('school', 'level')
    search_fields = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name', 'school', 'level')
        }),
        ('Programme Details', {
            'fields': (
                'description',
                'duration',
                'entry_requirements',
                'certification',
                'career_prospects',
            )
        }),
    )
