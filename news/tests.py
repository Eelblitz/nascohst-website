from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from news.models import News, Category


class NewsModelTests(TestCase):

    def test_slug_is_generated(self):
        article = News.objects.create(
            title="Testing Django Slug",
            content="<p>Hello World</p>",
        )

        self.assertEqual(article.slug, "testing-django-slug")

    def test_reading_time_returns_at_least_one(self):
        article = News.objects.create(
            title="Reading Time Test",
            content="<p>Hello World</p>",
        )

        self.assertGreaterEqual(article.reading_time(), 1)


class NewsViewsTests(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="Academic Articles"
        )

        self.article = News.objects.create(
            title="Sample Publication",
            content="<p>This is a publication.</p>",
            category=self.category,
            status=News.PUBLISHED,
        )

    def test_news_list_page_loads(self):
        response = self.client.get(
            reverse("news:news_list")
        )

        self.assertEqual(response.status_code, 200)

    def test_news_detail_page_loads(self):
        response = self.client.get(
            reverse(
                "news:news_detail_slug",
                kwargs={"slug": self.article.slug},
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_article_title_is_displayed(self):
        response = self.client.get(
            reverse(
                "news:news_detail_slug",
                kwargs={"slug": self.article.slug},
            )
        )

        self.assertContains(
            response,
            "Sample Publication",
        )

    def test_news_detail_page_emits_expected_csp_header(self):
        response = self.client.get(
            reverse(
                "news:news_detail_slug",
                kwargs={"slug": self.article.slug},
            )
        )

        csp = response.headers.get("Content-Security-Policy", "")

        self.assertIn("default-src 'self'", csp)
        self.assertIn("script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'", csp)
        self.assertIn("style-src 'self' https://fonts.googleapis.com 'unsafe-inline'", csp)
        self.assertIn("font-src 'self' https://fonts.gstatic.com", csp)
        self.assertIn("img-src 'self' data: https://res.cloudinary.com", csp)
