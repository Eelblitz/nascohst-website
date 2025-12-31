from django.db import models

class AboutPage(models.Model):
    history = models.TextField()
    vision = models.TextField()
    mission = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "About the College"

