from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from .models import News


def news_list(request):
    news_items = News.objects.filter(
        published_at__isnull=False,
        published_at__lte=now()
    ).order_by('-published_at')

    return render(request, 'news/news_list.html', {
        'news_items': news_items
    })


def news_detail(request, pk):
    news = get_object_or_404(
        News,
        pk=pk,
        published_at__isnull=False,
        published_at__lte=now()
    )

    return render(request, 'news/news_detail.html', {
        'news': news
    })
