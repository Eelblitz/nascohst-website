from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import SitePopup


class SitePopupTests(TestCase):
    def create_popup(self, **kwargs):
        defaults = {
            "title": "Admissions Open",
            "message": "Apply now.",
            "button_url": "/admissions/",
        }
        defaults.update(kwargs)
        return SitePopup.objects.create(**defaults)

    def test_homepage_context_has_no_popup_when_none_active(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["active_popup"])

    def test_inactive_popup_is_not_returned(self):
        self.create_popup(is_active=False)

        response = self.client.get(reverse("home"))

        self.assertIsNone(response.context["active_popup"])

    def test_date_filtering_respects_start_and_end_dates(self):
        now = timezone.now()
        eligible = self.create_popup(
            title="Eligible",
            is_active=True,
            start_date=now - timedelta(hours=1),
            end_date=now + timedelta(hours=1),
            display_order=5,
        )
        self.create_popup(
            title="Future",
            is_active=True,
            start_date=now + timedelta(hours=1),
            end_date=now + timedelta(days=1),
            display_order=0,
        )
        self.create_popup(
            title="Expired",
            is_active=True,
            start_date=now - timedelta(days=2),
            end_date=now - timedelta(hours=1),
            display_order=0,
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.context["active_popup"], eligible)

    def test_ordering_prefers_lowest_display_order(self):
        now = timezone.now()
        first = self.create_popup(
            title="First",
            is_active=True,
            start_date=now - timedelta(hours=1),
            end_date=now + timedelta(hours=1),
            display_order=0,
        )
        self.create_popup(
            title="Second",
            is_active=True,
            start_date=now - timedelta(hours=1),
            end_date=now + timedelta(hours=1),
            display_order=2,
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.context["active_popup"], first)

    def test_homepage_renders_popup_markup_when_active_popup_exists(self):
        now = timezone.now()
        self.create_popup(
            title="Notice",
            message="Read this.",
            button_url="/news/",
            is_active=True,
            start_date=now - timedelta(hours=1),
            end_date=now + timedelta(hours=1),
        )

        response = self.client.get(reverse("home"))

        self.assertContains(response, "homepagePopup")
        self.assertContains(response, "Read this.")
