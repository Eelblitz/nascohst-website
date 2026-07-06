from django.db import models


class AppraisalTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class AppraisalCategory(models.Model):
    template = models.ForeignKey(
        AppraisalTemplate,
        on_delete=models.CASCADE,
        related_name="categories"
    )

    title = models.CharField(max_length=100)

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.template.name} - {self.title}"


class AppraisalQuestion(models.Model):
    category = models.ForeignKey(
        AppraisalCategory,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question = models.TextField()

    max_score = models.PositiveIntegerField(default=5)

    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.question[:50]


class AppraisalCycle(models.Model):
    title = models.CharField(max_length=100)

    template = models.ForeignKey(
        AppraisalTemplate,
        on_delete=models.PROTECT
    )

    start_date = models.DateField()
    end_date = models.DateField()

    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title