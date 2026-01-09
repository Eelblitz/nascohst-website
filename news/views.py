from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from .models import News
from django.core.paginator import Paginator


def news_list(request):
    queryset = News.objects.filter(
        published_at__isnull=False,
        published_at__lte=now()
    ).order_by('-published_at')

    paginator = Paginator(queryset, 6)
    page_number = request.GET.get('page')
    news = paginator.get_page(page_number)

    return render(request, 'news/news_list.html', {
        'news': news
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
