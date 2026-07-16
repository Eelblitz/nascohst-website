from .models import News, Category, Comment
from .forms import CommentForm
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.db.models import Q, F, Count, Case, When, Value, IntegerField


CATEGORY_GROUP_ORDER = {
    "Institutional News": 0,
    "Academic Publications": 1,
    "Public Health": 2,
    "Clinical Sciences": 3,
    "Health Sciences Education": 4,
    "Technology & Innovation": 5,
    "Policy & Governance": 6,
    "Student Corner": 7,
}


def ordered_categories(queryset):
    return queryset.annotate(
        group_order=Case(
            *[
                When(name=name, then=Value(order))
                for name, order in CATEGORY_GROUP_ORDER.items()
            ],
            default=Value(999),
            output_field=IntegerField(),
        )
    ).order_by("group_order", "name")



def news_list(request):
    search_query = request.GET.get("q", "")
    category_slug = request.GET.get("category", "")

    queryset = (
        News.objects.filter(
            status=News.PUBLISHED,
            published_at__lte=now(),
        )
        .select_related("author", "category")
        .prefetch_related("publication_authors__staff")
        .order_by("-featured", "-published_at")
    )

    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query)
            | Q(excerpt__icontains=search_query)
            | Q(content__icontains=search_query)
            | Q(author__name__icontains=search_query)
            | Q(publication_authors__external_name__icontains=search_query)
            | Q(publication_authors__affiliation__icontains=search_query)
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

    categories = ordered_categories(Category.objects.all())
    popular_articles = (
        News.objects.filter(
            status=News.PUBLISHED,
            published_at__lte=now(),
        )
        .prefetch_related("publication_authors__staff")
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
            Q(author=news.author) |
            Q(publication_authors__external_name__in=[author.citation_name for author in news.author_list()])
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
            Q(author=news.author) |
            Q(publication_authors__external_name__in=[author.citation_name for author in news.author_list()])
        )
        .exclude(pk=news.pk)
        .distinct()[:3]
    )

    # Most read
    popular_articles = (
        News.objects.filter(status=News.PUBLISHED)
        .prefetch_related("publication_authors__staff")
        .exclude(pk=news.pk)
        .order_by("-views")[:5]
    )

    # Recent publications
    recent_articles = (
        News.objects.filter(status=News.PUBLISHED)
        .prefetch_related("publication_authors__staff")
        .exclude(pk=news.pk)
        .order_by("-published_at")[:5]
    )

    # Categories with article count
    categories = (
        ordered_categories(Category.objects.annotate(
            article_count=Count("articles")
        ))
    )

    # Latest approved comments
    latest_comments = (
        Comment.objects.filter(approved=True)
        .select_related("news")
        .order_by("-created_at")[:5]
    )

    # Approved comments for this article
    comments = news.comments.filter(
        approved=True
    )

    # Comment form
    comment_submitted = False

    if request.method == "POST":

        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)
            comment.news = news
            comment.save()

            comment_submitted = True

            form = CommentForm()

    else:

        form = CommentForm()

    return render(
        request,
        "news/news_detail.html",
        {
            "news": news,
            "previous_article": previous_article,
            "next_article": next_article,
            "related_articles": related_articles,
            "popular_articles": popular_articles,
            "recent_articles": recent_articles,
            "categories": categories,
            "latest_comments": latest_comments,
            "comments": comments,
            "comment_form": form,
            "comment_submitted": comment_submitted,
        },
    )
