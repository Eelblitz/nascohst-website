import math

from django.db import models
from django.utils.text import slugify
from django.utils.html import strip_tags
from django_ckeditor_5.fields import CKEditor5Field


# --------------------------------------------------
# Category Model
# --------------------------------------------------

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# --------------------------------------------------
# News / Publications Model
# --------------------------------------------------

class News(models.Model):

    DRAFT = "draft"
    PUBLISHED = "published"

    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (PUBLISHED, "Published"),
    ]

    title = models.CharField(max_length=200)

    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
    )

    excerpt = models.TextField(
        max_length=300,
        blank=True,
        help_text="Short summary displayed on the news listing page.",
    )

    content = CKEditor5Field(
        "Content",
        config_name="default",
    )

    image = models.ImageField(
        upload_to="news/",
        blank=True,
        null=True,
    )

    attachment = models.FileField(
        upload_to="news/documents/",
        blank=True,
        null=True,
        help_text="Upload a PDF, journal, circular or official document.",
    )

    author = models.ForeignKey(
        "staff.Staff",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        help_text="Staff member who authored this article.",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    featured = models.BooleanField(
        default=False,
        help_text="Display this article in featured sections.",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PUBLISHED,
    )

    published_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    views = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this publication has been viewed.",
    )

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "News Article"
        verbose_name_plural = "News Articles"

    def save(self, *args, **kwargs):

        # Generate unique slug
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while News.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        # Always generate a clean excerpt from the content
        plain_text = strip_tags(self.content).strip()

        if len(plain_text) > 300:
            self.excerpt = plain_text[:297].rstrip() + "..."
        else:
            self.excerpt = plain_text

        super().save(*args, **kwargs)

    def reading_time(self):
        """
        Estimate reading time based on 200 words per minute.
        """
        if not self.content:
            return 1

        words = len(strip_tags(self.content).split())
        return max(1, math.ceil(words / 200))

    def __str__(self):
        return self.title
    
    # --------------------------------------------------
# Comments
# --------------------------------------------------

class Comment(models.Model):
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    name = models.CharField(
        max_length=100,
    )

    email = models.EmailField()

    body = models.TextField(
        verbose_name="Comment",
    )

    approved = models.BooleanField(
        default=False,
        help_text="Approved comments are visible to the public.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"{self.name} on {self.news.title}"