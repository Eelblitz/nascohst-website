from django.shortcuts import render
from django.http import HttpResponse
from django.utils.timezone import now
from datetime import datetime

from django.db.utils import OperationalError, ProgrammingError

from staff.models import Staff
from academics.models import Programme
from news.models import News
from .models import AboutPage


def robots_txt(request):
    return HttpResponse(
        open('templates/robots.txt').read(),
        content_type='text/plain'
    )


def home(request):
    year = datetime.now().year

    # Defaults that never crash
    management_staff = []
    search_data = []

    try:
        # --- Management staff ---
        management_staff = (
            Staff.objects
            .filter(category=Staff.MANAGEMENT, is_approved=True)
            .order_by('display_order')[:4]
        )

        # --- Staff search ---
        for staff in Staff.objects.filter(is_approved=True):
            search_data.append({
                "label": f"{staff.name} – {staff.designation}",
                "url": "/staff/"
            })

        # --- Programmes ---
        for programme in Programme.objects.select_related('school'):
            search_data.append({
                "label": f"{programme.name} ({programme.level})",
                "url": f"/academics/{programme.school.id}/"
            })

        # --- News ---
        for item in News.objects.filter(
            published_at__isnull=False,
            published_at__lte=now()
        ):
            search_data.append({
                "label": item.title,
                "url": f"/news/{item.id}/"
            })

    except (OperationalError, ProgrammingError):
        # Database not ready yet (migrations, fresh deploy, new DB)
        # Site must still load
        pass

    return render(request, 'core/home.html', {
        'management_staff': management_staff,
        'search_data': search_data,
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
