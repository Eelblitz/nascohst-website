from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.utils.timezone import now

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
    # --- Management staff for homepage ---
    management_staff = Staff.objects.filter(
        category=Staff.MANAGEMENT,
        is_approved=True
    ).order_by('display_order')[:4]

    # --- Global search data ---
    search_data = []

    # Staff (approved only)
    staff_qs = Staff.objects.filter(is_approved=True)
    for staff in staff_qs:
        search_data.append({
            "label": f"{staff.name} – {staff.designation}",
            "url": "/staff/"
        })

    # Academic programmes
    programme_qs = Programme.objects.select_related('school')
    for programme in programme_qs:
        search_data.append({
            "label": f"{programme.name} ({programme.level})",
            "url": f"/academics/{programme.school.id}/"
        })

    # News (published only)
    news_qs = News.objects.filter(
        published_at__isnull=False,
        published_at__lte=now()
    )
    for item in news_qs:
        search_data.append({
            "label": item.title,
            "url": f"/news/{item.id}/"
        })

    return render(request, 'core/home.html', {
        'management_staff': management_staff,
        'search_data': search_data,
        'year': datetime.now().year,
    })


def about(request):
    about = AboutPage.objects.first()
    return render(request, 'core/about.html', {
        'about': about,
        'year': datetime.now().year,
    })


def contact(request):
    return render(request, 'core/contact.html', {
        'year': datetime.now().year,
    })

from staff.models import Staff
from datetime import datetime

def admissions(request):
    admissions_officer = Staff.objects.filter(
        category=Staff.MANAGEMENT,
        designation__icontains="admission",
        is_approved=True
    ).first()

    return render(request, 'core/admissions.html', {
        'admissions_officer': admissions_officer,
        'year': datetime.now().year,
    })
