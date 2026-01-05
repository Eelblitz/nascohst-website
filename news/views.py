from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from .models import News


def news_list(request):
    news = News.objects.filter(
        published_at__isnull=False,
        published_at__lte=now()
    ).order_by('-published_at')

    return render(request, 'news/news_list.html', {
        'news': news
    })


def news_detail(request, pk):
    item = get_object_or_404(
        News,
        pk=pk,
        published_at__isnull=False
    )

    return render(request, 'news/news_detail.html', {
        'item': item
    })
