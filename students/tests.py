from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from academics.models import Programme, School

from .models import Student


class StudentAnalyticsDashboardTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password123",
        )
        self.client.force_login(self.user)

        self.school = School.objects.create(
            name="School of Health Sciences",
            description="Health sciences school",
        )
        self.programme = Programme.objects.create(
            name="Nursing Science",
            school=self.school,
            level="ND",
        )

        Student.objects.create(
            matriculation_number="NAS/2026/001",
            index_number="IDX001",
            last_name="Adebayo",
            other_names="Kemi",
            programme=self.programme,
            level="ND I",
            gender="F",
        )
        Student.objects.create(
            matriculation_number="NAS/2026/002",
            index_number="IDX002",
            last_name="Ibrahim",
            other_names="Bello",
            programme=self.programme,
            level="ND I",
            gender="M",
            graduation_year=2025,
        )

    def test_admin_analytics_dashboard_reads_live_student_data(self):
        response = self.client.get(reverse("admin:students_student_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_students"], 2)
        self.assertEqual(response.context["current_students"], 1)
        self.assertEqual(response.context["alumni"], 1)
        self.assertEqual(response.context["recent_registrations"], 2)
        self.assertEqual(list(response.context["by_level"])[0]["total"], 2)
        self.assertEqual(list(response.context["by_gender"])[0]["total"], 1)
        self.assertEqual(list(response.context["by_school"])[0]["total"], 2)
        self.assertEqual(list(response.context["by_programme"])[0]["total"], 2)
