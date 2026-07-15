import math

from django.db import models
from django.core.exceptions import ValidationError
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
        self._sync_legacy_author()

    def _sync_legacy_author(self):
        if not self.author_id:
            return

        if self.publication_authors.exists():
            return

        PublicationAuthor.objects.create(
            publication=self,
            staff=self.author,
            external_name=self.author.name,
            affiliation=self.author.department,
            is_primary=True,
            is_corresponding=True,
            display_order=1,
        )

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

    def primary_author(self):
        author = self.publication_authors.select_related("staff").filter(is_primary=True).order_by("display_order").first()
        if author:
            return author
        return self.publication_authors.select_related("staff").order_by("display_order").first()

    def corresponding_author(self):
        author = self.publication_authors.select_related("staff").filter(is_corresponding=True).order_by("display_order").first()
        if author:
            return author
        return self.primary_author()

    def author_list(self):
        return self.publication_authors.select_related("staff").order_by("display_order", "id")

    def citation_authors(self):
        authors = list(self.author_list())
        names = [author.citation_name for author in authors]
        if not names and self.author:
            names = [self.author.name]
        return self._format_citation_names(names)

    def has_external_authors(self):
        return self.publication_authors.filter(staff__isnull=True).exists()

    @staticmethod
    def _format_citation_names(names):
        if not names:
            return ""
        if len(names) == 1:
            return names[0]
        if len(names) == 2:
            return f"{names[0]} and {names[1]}"
        return f"{', '.join(names[:-1])}, and {names[-1]}"


class PublicationAuthor(models.Model):
    publication = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name="publication_authors",
    )
    staff = models.ForeignKey(
        "staff.Staff",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publication_authorships",
    )
    external_name = models.CharField(max_length=200)
    affiliation = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    orcid = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    is_corresponding = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "Publication Author"
        verbose_name_plural = "Publication Authors"
        constraints = [
            models.UniqueConstraint(
                fields=["publication"],
                condition=models.Q(is_corresponding=True),
                name="unique_corresponding_author_per_publication",
            ),
        ]

    def clean(self):
        super().clean()
        if self.is_corresponding and self.publication_id:
            conflict = PublicationAuthor.objects.filter(
                publication=self.publication,
                is_corresponding=True,
            ).exclude(pk=self.pk)
            if conflict.exists():
                raise ValidationError({"is_corresponding": "Only one corresponding author is allowed per publication."})

    def save(self, *args, **kwargs):
        if self.staff and not self.external_name:
            self.external_name = self.staff.name
        if self.staff and not self.affiliation:
            self.affiliation = self.staff.department
        if not self.external_name:
            raise ValidationError({"external_name": "Author name is required."})
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def citation_name(self):
        if self.staff:
            return self.staff.name
        return self.external_name

    def __str__(self):
        return self.citation_name

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
