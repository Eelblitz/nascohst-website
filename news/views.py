from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.utils.timezone import now

from .models import News, Category


def news_list(request):
    queryset = (
        News.objects.filter(
            status=News.PUBLISHED,
            published_at__lte=now(),
        )
        .select_related("author", "category")
        .order_by("-featured", "-published_at")
    )

    paginator = Paginator(queryset, 6)
    page_number = request.GET.get("page")
    news = paginator.get_page(page_number)

    featured_article = queryset.filter(featured=True).first()

    categories = Category.objects.all()

    return render(
        request,
        "news/news_list.html",
        {
            "news": news,
            "featured_article": featured_article,
            "categories": categories,
        },
    )


def news_detail(request, pk):
    article = get_object_or_404(
        News.objects.select_related("author", "category"),
        pk=pk,
        status=News.PUBLISHED,
    )

    related_articles = (
        News.objects.filter(
            category=article.category,
            status=News.PUBLISHED,
        )
        .exclude(pk=article.pk)
        .select_related("author", "category")[:3]
    )

    return render(
        request,
        "news/news_detail.html",
        {
            "news": article,
            "related_articles": related_articles,
        },
    )