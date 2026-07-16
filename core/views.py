from django.shortcuts import render
from django.http import HttpResponse
from django.utils.timezone import now
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime

from django.db.utils import OperationalError, ProgrammingError
from django.db.models import Q

from staff.models import Staff
from academics.models import Programme
from news.models import News
from .models import AboutPage, SitePopup


def robots_txt(request):
    return render(request, 'robots.txt', content_type='text/plain')


def home(request):
    year = datetime.now().year
    current_time = timezone.now()

    management_staff = []
    search_data = []
    latest_news = []
    active_popup = None

    try:
        management_staff = cache.get_or_set(
            'home_management_staff',
            lambda: list(
                Staff.objects
                .filter(category=Staff.MANAGEMENT, is_approved=True)
                .order_by('display_order')[:4]
            ),
            300,
        )

        for staff in Staff.objects.filter(is_approved=True):
            search_data.append({
                "label": f"{staff.name} – {staff.designation}",
                "url": "/staff/"
            })

        for programme in Programme.objects.select_related('school'):
            search_data.append({
                "label": f"{programme.name} ({programme.level})",
                "url": f"/academics/{programme.school.id}/"
            })

        latest_news = cache.get_or_set(
            'home_latest_news',
            lambda: list(
                News.objects
                .filter(published_at__isnull=False, published_at__lte=now())
                .order_by('-published_at')[:3]
            ),
            300,
        )

        for item in latest_news:
            search_data.append({
                "label": item.title,
                "url": f"/news/{item.id}/"
            })

        popup_qs = SitePopup.objects.filter(
            is_active=True
        ).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=current_time),
            Q(end_date__isnull=True) | Q(end_date__gte=current_time),
        )
        active_popup = popup_qs.order_by('display_order', '-created_at').first()

    except (OperationalError, ProgrammingError):
        pass

    return render(request, 'core/home.html', {
        'management_staff': management_staff,
        'search_data': search_data,
        'latest_news': latest_news,
        'active_popup': active_popup,
        'year': year,
    })


def about(request):
    year = datetime.now().year
    about = None

    try:
        about = AboutPage.objects.first()
    except (OperationalError, ProgrammingError):
        pass

    return render(request, 'core/about.html', {
        'about': about,
        'year': year,
    })


def contact(request):
    return render(request, 'core/contact.html', {
        'year': datetime.now().year,
    })


def admissions(request):
    year = datetime.now().year
    admissions_officer = None

    try:
        admissions_officer = Staff.objects.filter(
            category=Staff.MANAGEMENT,
            designation__icontains="admission",
            is_approved=True
        ).first()
    except (OperationalError, ProgrammingError):
        pass

    return render(request, 'core/admissions.html', {
        'admissions_officer': admissions_officer,
        'year': year,
    })


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')


def terms_of_use(request):
    return render(request, 'core/terms_of_use.html')


def admissions_disclaimer(request):
    return render(request, 'core/admissions_disclaimer.html')
