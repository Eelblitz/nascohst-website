from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.db.models import Q, F

from .models import News, Category


def news_list(request):
    search_query = request.GET.get("q", "")
    category_slug = request.GET.get("category", "")

    queryset = (
        News.objects.filter(
            status=News.PUBLISHED,
            published_at__lte=now(),
        )
        .select_related("author", "category")
        .order_by("-featured", "-published_at")
    )

    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query)
            | Q(excerpt__icontains=search_query)
            | Q(content__icontains=search_query)
            | Q(author__name__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)

    featured_article = queryset.filter(featured=True).first()

    if featured_article:
        queryset = queryset.exclude(pk=featured_article.pk)

    paginator = Paginator(queryset, 6)
    page_number = request.GET.get("page")
    news = paginator.get_page(page_number)

    categories = Category.objects.all()
    popular_articles = (
        News.objects.filter(
            status=News.PUBLISHED,
            published_at__lte=now(),
        )
        .exclude(pk=featured_article.pk if featured_article else None)
        .order_by("-views")[:5]
    )

    return render(
        request,
        "news/news_list.html",
        {
            "news": news,
            "featured_article": featured_article,
            "popular_articles": popular_articles,
            "categories": categories,
            "search_query": search_query,
            "selected_category": category_slug,
        },
    )

def news_detail(request, pk):

    news = get_object_or_404(
        News,
        pk=pk,
        status=News.PUBLISHED,
        published_at__lte=now(),
    )
    previous_article = (
        News.objects.filter(
            status=News.PUBLISHED,
            published_at__lt=news.published_at
        )
        .order_by("-published_at")
        .first()
    )

    next_article = (
        News.objects.filter(
            status=News.PUBLISHED,
            published_at__gt=news.published_at
        )
        .order_by("published_at")
        .first()
    )
    News.objects.filter(pk=news.pk).update(
        views=F("views") + 1
    )

    news.refresh_from_db()

    related_articles = (
        News.objects.filter(status=News.PUBLISHED)
        .filter(
            Q(category=news.category) |
            Q(author=news.author)
        )
        .exclude(pk=news.pk)
        .distinct()[:3]
    )

    return render(
        request,
        "news/news_detail.html",
        {
            "news": news,
            "related_articles": related_articles,
            "previous_article": previous_article,
            "next_article": next_article,
        },
    )


def news_detail_slug(request, slug):

    news = get_object_or_404(
        News,
        slug=slug,
        status=News.PUBLISHED,
        published_at__lte=now(),
    )

    # Increment views
    News.objects.filter(pk=news.pk).update(
        views=F("views") + 1
    )

    news.refresh_from_db()

    # Previous publication
    previous_article = (
        News.objects.filter(
            status=News.PUBLISHED,
            published_at__lt=news.published_at,
        )
        .order_by("-published_at")
        .first()
    )

    # Next publication
    next_article = (
        News.objects.filter(
            status=News.PUBLISHED,
            published_at__gt=news.published_at,
        )
        .order_by("published_at")
        .first()
    )

    # Related publications
    related_articles = (
        News.objects.filter(status=News.PUBLISHED)
        .filter(
            Q(category=news.category) |
            Q(author=news.author)
        )
        .exclude(pk=news.pk)
        .distinct()[:3]
    )

    return render(
        request,
        "news/news_detail.html",
        {
            "news": news,
            "related_articles": related_articles,
            "previous_article": previous_article,
            "next_article": next_article,
        },
    )