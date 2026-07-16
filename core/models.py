from django.db import models


class AboutPage(models.Model):
    history = models.TextField()
    vision = models.TextField()
    mission = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "About the College"


class SitePopup(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    image = models.ImageField(upload_to="popups/", blank=True, null=True)
    button_text = models.CharField(max_length=50, default="Learn More")
    button_url = models.CharField(max_length=300)
    is_active = models.BooleanField(default=False)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.title

