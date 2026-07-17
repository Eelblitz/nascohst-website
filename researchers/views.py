from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Researcher


def researcher_list(request):
    search_query = request.GET.get("q", "").strip()
    institution = request.GET.get("institution", "").strip()
    department = request.GET.get("department", "").strip()
    country = request.GET.get("country", "").strip()
    researcher_type = request.GET.get("type", "").strip()
    ordering = request.GET.get("ordering", "alphabetical").strip()
    querystring = request.GET.copy()
    querystring.pop("page", None)

    queryset = Researcher.objects.select_related("staff").annotate(
        publication_count_total=Count("publication_authorships", distinct=True)
    )

    if search_query:
        queryset = queryset.filter(
            Q(display_name__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(middle_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(institution__icontains=search_query)
            | Q(department__icontains=search_query)
            | Q(research_interests__icontains=search_query)
            | Q(biography__icontains=search_query)
        )

    if institution:
        queryset = queryset.filter(institution__icontains=institution)
    if department:
        queryset = queryset.filter(department__icontains=department)
    if country:
        queryset = queryset.filter(country__icontains=country)
    if researcher_type == "internal":
        queryset = queryset.filter(is_internal=True)
    elif researcher_type == "external":
        queryset = queryset.filter(is_internal=False)

    if ordering == "most_publications":
        queryset = queryset.order_by("-publication_count_total", "display_name")
    elif ordering == "recently_joined":
        queryset = queryset.order_by("-joined_at", "display_name")
    else:
        queryset = queryset.order_by("display_name")

    institutions = Researcher.objects.exclude(institution="").values_list("institution", flat=True).distinct().order_by("institution")
    departments = Researcher.objects.exclude(department="").values_list("department", flat=True).distinct().order_by("department")
    countries = Researcher.objects.exclude(country="").values_list("country", flat=True).distinct().order_by("country")

    paginator = Paginator(queryset, 9)
    page_number = request.GET.get("page")
    researchers = paginator.get_page(page_number)

    return render(
        request,
        "researchers/researcher_list.html",
        {
            "researchers": researchers,
            "search_query": search_query,
            "selected_institution": institution,
            "selected_department": department,
            "selected_country": country,
            "selected_type": researcher_type,
            "selected_ordering": ordering,
            "querystring": querystring.urlencode(),
            "institutions": institutions,
            "departments": departments,
            "countries": countries,
        },
    )


def researcher_detail(request, slug):
    researcher = get_object_or_404(
        Researcher.objects.select_related("staff").annotate(
            publication_count_total=Count("publication_authorships", distinct=True)
        ),
        slug=slug,
    )
    publications = (
        researcher.publication_authorships.select_related("publication", "publication__category")
        .order_by("-publication__published_at", "display_order", "id")
    )

    return render(
        request,
        "researchers/researcher_detail.html",
        {
            "researcher": researcher,
            "publications": publications,
        },
    )
