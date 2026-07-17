from django.test import TestCase
from django.urls import reverse

from news.models import News, PublicationAuthor
from staff.models import Staff
from researchers.models import Researcher


class ResearcherModelTests(TestCase):
    def test_slug_is_generated(self):
        researcher = Researcher.objects.create(
            first_name="Ada",
            last_name="Lovelace",
            display_name="Ada Lovelace",
        )
        self.assertEqual(researcher.slug, "ada-lovelace")

    def test_slug_is_unique(self):
        first = Researcher.objects.create(display_name="Researcher One")
        second = Researcher.objects.create(display_name="Researcher One")

        self.assertEqual(first.slug, "researcher-one")
        self.assertEqual(second.slug, "researcher-one-1")

    def test_internal_researcher_syncs_from_staff(self):
        staff = Staff.objects.create(
            name="Dr. Internal",
            designation="Senior Lecturer",
            department="Public Health",
            qualifications="PhD",
            biography="Staff biography",
            category=Staff.ACADEMIC,
            is_approved=True,
        )
        researcher = Researcher.objects.create(staff=staff, is_internal=True)

        self.assertEqual(researcher.display_name, "Dr. Internal")
        self.assertEqual(researcher.department, "Public Health")
        self.assertEqual(researcher.biography, "Staff biography")
        self.assertTrue(researcher.is_internal)
        self.assertEqual(researcher.full_name, "Senior Lecturer Dr. Internal")

    def test_external_researcher_does_not_require_staff(self):
        researcher = Researcher.objects.create(
            title="Prof.",
            first_name="External",
            last_name="Scholar",
            display_name="Prof. External Scholar",
            institution="Independent Institute",
            is_internal=False,
        )

        self.assertIsNone(researcher.staff)
        self.assertEqual(researcher.display_name, "Prof. External Scholar")


class ResearcherViewTests(TestCase):
    def setUp(self):
        self.staff = Staff.objects.create(
            name="Dr. Researcher",
            designation="Lecturer",
            department="Public Health",
            qualifications="PhD",
            biography="Staff bio",
            category=Staff.ACADEMIC,
            is_approved=True,
        )
        self.researcher = Researcher.objects.create(
            staff=self.staff,
            is_internal=True,
            country="Nigeria",
            institution="NASCOHST",
        )
        self.external_researcher = Researcher.objects.create(
            display_name="Dr. External Scholar",
            institution="Independent Institute",
            country="Ghana",
            is_internal=False,
        )
        article = News.objects.create(
            title="Research Output",
            content="<p>Body</p>",
        )
        PublicationAuthor.objects.create(
            publication=article,
            researcher=self.researcher,
            external_name=self.researcher.display_name,
            affiliation=self.researcher.institution,
            is_primary=True,
        )

    def test_researcher_list_page_loads(self):
        response = self.client.get(reverse("researchers:researcher_list"))
        self.assertEqual(response.status_code, 200)

    def test_researcher_list_search_and_filters(self):
        response = self.client.get(
            reverse("researchers:researcher_list"),
            {"q": "Dr. External", "type": "external", "country": "Ghana"},
        )
        self.assertContains(response, "Dr. External Scholar")
        self.assertNotContains(response, "Dr. Researcher")

    def test_researcher_detail_page_loads(self):
        response = self.client.get(
            reverse("researchers:researcher_detail", kwargs={"slug": self.researcher.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.researcher.display_name)
        self.assertContains(response, "Research Output")

    def test_publication_author_links_to_researcher_profile(self):
        article = News.objects.first()
        author = article.primary_author()

        self.assertEqual(
            reverse("researchers:researcher_detail", kwargs={"slug": self.researcher.slug}),
            f"/researchers/{self.researcher.slug}/",
        )
        self.assertEqual(author.citation_name, "Dr. Researcher")
