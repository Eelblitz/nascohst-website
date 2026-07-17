from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from news.models import News, Category, PublicationAuthor
from researchers.models import Researcher
from staff.models import Staff


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

    def test_publication_authors_are_ordered(self):
        staff_a = Staff.objects.create(
            name="Dr. Alpha",
            designation="Lecturer",
            department="Community Health",
            qualifications="MBBS",
            category=Staff.ACADEMIC,
            is_approved=True,
        )
        staff_b = Staff.objects.create(
            name="Dr. Beta",
            designation="Lecturer",
            department="Community Health",
            qualifications="MBBS",
            category=Staff.ACADEMIC,
            is_approved=True,
        )
        article = News.objects.create(
            title="Authorship Order",
            content="<p>Body</p>",
        )
        PublicationAuthor.objects.create(
            publication=article,
            staff=staff_b,
            external_name=staff_b.name,
            affiliation=staff_b.department,
            display_order=2,
        )
        PublicationAuthor.objects.create(
            publication=article,
            staff=staff_a,
            external_name=staff_a.name,
            affiliation=staff_a.department,
            display_order=1,
            is_primary=True,
        )

        self.assertEqual(
            [author.citation_name for author in article.author_list()],
            ["Dr. Alpha", "Dr. Beta"],
        )
        self.assertEqual(article.primary_author().citation_name, "Dr. Alpha")

    def test_publication_author_syncs_from_legacy_author(self):
        staff = Staff.objects.create(
            name="Dr. Legacy",
            designation="Lecturer",
            department="Epidemiology",
            qualifications="MBBS",
            category=Staff.ACADEMIC,
            is_approved=True,
        )
        article = News.objects.create(
            title="Legacy Author",
            content="<p>Body</p>",
            author=staff,
        )
        article.ensure_legacy_publication_author()

        self.assertEqual(article.publication_authors.count(), 1)
        author = article.publication_authors.first()
        self.assertTrue(author.is_primary)
        self.assertTrue(author.is_corresponding)
        self.assertEqual(author.citation_name, "Dr. Legacy")

    def test_citation_authors_formatting(self):
        article = News.objects.create(
            title="Citation Formatting",
            content="<p>Body</p>",
        )
        staff = Staff.objects.create(
            name="Dr. Citation",
            designation="Lecturer",
            department="Public Health",
            qualifications="MBBS",
            category=Staff.ACADEMIC,
            is_approved=True,
        )
        PublicationAuthor.objects.create(
            publication=article,
            staff=staff,
            external_name=staff.name,
            affiliation=staff.department,
            is_primary=True,
        )

        self.assertEqual(article.citation_authors(), "Dr. Citation")

    def test_corresponding_author_selection(self):
        article = News.objects.create(
            title="Corresponding Author",
            content="<p>Body</p>",
        )
        staff_primary = Staff.objects.create(
            name="Dr. Primary",
            designation="Lecturer",
            department="Public Health",
            qualifications="MBBS",
            category=Staff.ACADEMIC,
            is_approved=True,
        )
        staff_corresponding = Staff.objects.create(
            name="Dr. Contact",
            designation="Lecturer",
            department="Public Health",
            qualifications="MBBS",
            category=Staff.ACADEMIC,
            is_approved=True,
        )

        PublicationAuthor.objects.create(
            publication=article,
            staff=staff_primary,
            external_name=staff_primary.name,
            affiliation=staff_primary.department,
            display_order=1,
            is_primary=True,
        )
        PublicationAuthor.objects.create(
            publication=article,
            staff=staff_corresponding,
            external_name=staff_corresponding.name,
            affiliation=staff_corresponding.department,
            display_order=2,
            is_corresponding=True,
        )

        self.assertEqual(article.corresponding_author().citation_name, "Dr. Contact")

    def test_publication_author_prefers_researcher_profile(self):
        researcher = Researcher.objects.create(
            display_name="Dr. Research Profile",
            institution="NASCOHST",
            department="Community Health",
            is_internal=False,
        )
        article = News.objects.create(
            title="Researcher Authorship",
            content="<p>Body</p>",
        )
        author = PublicationAuthor.objects.create(
            publication=article,
            researcher=researcher,
            external_name="Fallback Name",
            affiliation="Fallback Affiliation",
            display_order=1,
            is_primary=True,
        )

        self.assertEqual(author.citation_name, "Dr. Research Profile")
        self.assertEqual(author.external_name, "Fallback Name")
        self.assertEqual(author.affiliation, "Fallback Affiliation")
        self.assertEqual(article.primary_author().citation_name, "Dr. Research Profile")


class NewsViewsTests(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="Academic Articles"
        )
        self.staff = Staff.objects.create(
            name="Dr. Sample",
            designation="Lecturer",
            department="Public Health",
            qualifications="MBBS",
            category=Staff.ACADEMIC,
            is_approved=True,
        )

        self.article = News.objects.create(
            title="Sample Publication",
            content="<p>This is a publication.</p>",
            category=self.category,
            status=News.PUBLISHED,
            author=self.staff,
        )
        self.article.ensure_legacy_publication_author()

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

    def test_news_detail_page_shows_comments_and_share_links(self):
        response = self.client.get(
            reverse(
                "news:news_detail_slug",
                kwargs={"slug": self.article.slug},
            )
        )

        self.assertContains(response, "Comments")
        self.assertContains(response, "Leave a comment")
        self.assertContains(response, "Submit Comment")
        self.assertContains(response, "WhatsApp")
        self.assertContains(response, "LinkedIn")
        self.assertContains(response, "Facebook")
        self.assertContains(response, "Instagram")
        self.assertContains(response, "X")

    def test_news_detail_page_shows_primary_author(self):
        response = self.client.get(
            reverse(
                "news:news_detail_slug",
                kwargs={"slug": self.article.slug},
            )
        )

        self.assertContains(response, "Primary Author")
        self.assertContains(response, "Authors &amp; Affiliations")
        self.assertEqual(self.article.publication_authors.count(), 1)
