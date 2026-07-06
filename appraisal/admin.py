from django.contrib import admin
from .models import (
    AppraisalTemplate,
    AppraisalCategory,
    AppraisalQuestion,
    AppraisalCycle,
)


@admin.register(AppraisalTemplate)
class AppraisalTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "created_at",
    )


@admin.register(AppraisalCategory)
class AppraisalCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "template",
        "weight",
    )


@admin.register(AppraisalQuestion)
class AppraisalQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "category",
        "max_score",
    )
    

@admin.register(AppraisalCycle)
class AppraisalCycleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "template",
        "start_date",
        "end_date",
        "is_active",
    )

    list_filter = (
        "is_active",
    )