from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from news.models import Category
from researchers.models import Researcher
from staff.models import Staff

from .forms import SubmissionAuthorForm, SubmissionForm
from .models import Submission, SubmissionAuthor, SubmissionFile


User = get_user_model()


class SubmissionModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Journal Articles")

    def test_slug_is_generated(self):
        submission = Submission.objects.create(
            title="Manuscript One",
            abstract="Abstract text",
            category=self.category,
        )
        self.assertEqual(submission.slug, "manuscript-one")

    def test_slug_is_unique(self):
        first = Submission.objects.create(
            title="Manuscript One",
            abstract="Abstract text",
        )
        second = Submission.objects.create(
            title="Manuscript One",
            abstract="Abstract text",
        )

        self.assertEqual(first.slug, "manuscript-one")
        self.assertEqual(second.slug, "manuscript-one-1")

    def test_submission_author_prefers_researcher_profile(self):
        researcher = Researcher.objects.create(display_name="Dr. Submission Researcher")
        submission = Submission.objects.create(
            title="Research Manuscript",
            abstract="Abstract text",
        )

        author = SubmissionAuthor.objects.create(
            submission=submission,
            researcher=researcher,
            external_name="Fallback Name",
            affiliation="Fallback Affiliation",
            is_primary=True,
        )

        self.assertEqual(author.citation_name, "Dr. Submission Researcher")
        self.assertEqual(author.external_name, "Fallback Name")
        self.assertEqual(author.affiliation, "Fallback Affiliation")

    def test_submission_file_string_representation(self):
        submission = Submission.objects.create(
            title="File Submission",
            abstract="Abstract text",
        )
        upload = SimpleUploadedFile("manuscript.pdf", b"dummy-content", content_type="application/pdf")
        submission_file = SubmissionFile.objects.create(
            submission=submission,
            file=upload,
            file_type=SubmissionFile.MAIN_MANUSCRIPT,
        )

        self.assertIn("File Submission", str(submission_file))
        self.assertIn("Main Manuscript", str(submission_file))


class SubmissionFormTests(TestCase):
    def test_submitted_submission_requires_title_and_abstract(self):
        form = SubmissionForm(
            data={
                "title": "",
                "slug": "",
                "abstract": "",
                "keywords": "",
                "submission_type": "",
                "category": "",
                "status": Submission.SUBMITTED,
                "cover_letter": "",
                "funding_information": "",
                "ethical_approval": "",
                "conflict_of_interest": "",
                "acknowledgements": "",
                "notes_to_editor": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("abstract", form.errors)

    def test_submission_author_form_requires_name_or_profile(self):
        form = SubmissionAuthorForm(
            data={
                "researcher": "",
                "staff": "",
                "external_name": "",
                "author_order": 1,
                "is_primary": True,
                "is_corresponding": False,
                "affiliation": "",
                "email": "",
                "orcid": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)


class SubmissionViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="researcher",
            email="researcher@example.com",
            password="testpass123",
        )
        self.staff = Staff.objects.create(
            name="Dr. Researcher",
            designation="Lecturer",
            department="Public Health",
            qualifications="PhD",
            category=Staff.ACADEMIC,
            is_approved=True,
            user=self.user,
        )
        self.researcher = Researcher.objects.create(
            user=self.user,
            staff=self.staff,
            is_internal=True,
            display_name="Dr. Researcher",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="testpass123",
        )
        self.other_staff = Staff.objects.create(
            name="Dr. Other",
            designation="Lecturer",
            department="Public Health",
            qualifications="PhD",
            category=Staff.ACADEMIC,
            is_approved=True,
            user=self.other_user,
        )
        self.other_researcher = Researcher.objects.create(
            user=self.other_user,
            staff=self.other_staff,
            is_internal=True,
            display_name="Dr. Other",
        )
        self.submission = Submission.objects.create(
            title="Draft Manuscript",
            abstract="Draft abstract",
            status=Submission.DRAFT,
        )
        self.author = SubmissionAuthor.objects.create(
            submission=self.submission,
            researcher=self.researcher,
            external_name=self.researcher.display_name,
            affiliation="NASCOHST",
            is_primary=True,
            is_corresponding=True,
        )
        self.submission.corresponding_author = self.author
        self.submission.save(update_fields=["corresponding_author"])

    def test_anonymous_users_are_redirected(self):
        response = self.client.get(reverse("submissions:submission_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_dashboard_loads_for_authenticated_researcher(self):
        self.client.login(username="researcher", password="testpass123")
        response = self.client.get(reverse("submissions:submission_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Submissions")
        self.assertContains(response, self.submission.title)

    def test_submission_detail_loads_for_owner(self):
        self.client.login(username="researcher", password="testpass123")
        response = self.client.get(
            reverse("submissions:submission_detail", kwargs={"pk": self.submission.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.submission.title)

    def test_submission_detail_denies_other_researcher(self):
        self.client.login(username="other", password="testpass123")
        response = self.client.get(
            reverse("submissions:submission_detail", kwargs={"pk": self.submission.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_submission_create_page_loads(self):
        self.client.login(username="researcher", password="testpass123")
        response = self.client.get(reverse("submissions:submission_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New Submission")

    def test_submission_edit_denies_submitted_manuscripts(self):
        self.submission.status = Submission.SUBMITTED
        self.submission.save()
        self.client.login(username="researcher", password="testpass123")
        response = self.client.get(
            reverse("submissions:submission_edit", kwargs={"pk": self.submission.pk})
        )
        self.assertEqual(response.status_code, 403)

