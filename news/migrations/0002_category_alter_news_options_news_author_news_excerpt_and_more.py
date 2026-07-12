# news/migrations/0002_category_alter_news_options_news_author_news_excerpt_and_more.py

from django.db import migrations, models
import django.db.models.deletion
from django.utils.text import slugify

def populate_news_slugs(apps, schema_editor):
    News = apps.get_model('news', 'News')
    for news_item in News.objects.all():
        if not getattr(news_item, 'slug', None):
            base_slug = slugify(news_item.title) if news_item.title else f'news-item-{news_item.pk}'
            unique_slug = base_slug
            counter = 1
            while News.objects.filter(slug=unique_slug).exclude(pk=news_item.pk).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            news_item.slug = unique_slug
            news_item.save()

class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0005_alter_staff_biography_alter_staff_display_order_and_more'),
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=120, unique=True)),
            ],
            options={'verbose_name_plural': 'Categories', 'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='news',
            options={'ordering': ['-published_at'], 'verbose_name': 'News Article', 'verbose_name_plural': 'News Articles'},
        ),
        migrations.AddField(
            model_name='news',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articles', to='staff.staff'),
        ),
        migrations.AddField(
            model_name='news',
            name='excerpt',
            field=models.TextField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name='news',
            name='featured',
            field=models.BooleanField(default=False),
        ),
        # 1. Add as a plain CharField first (prevents auto-creating SlugField indexes)
        migrations.AddField(
            model_name='news',
            name='slug',
            field=models.CharField(max_length=220, null=True, blank=True),
        ),
        # 2. Populate the data
        migrations.RunPython(populate_news_slugs, migrations.RunPython.noop),
        # 3. Now convert it to a unique SlugField
        migrations.AlterField(
            model_name='news',
            name='slug',
            field=models.SlugField(max_length=220, unique=True, null=False),
        ),
        migrations.AddField(
            model_name='news',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('published', 'Published')], default='published', max_length=20),
        ),
        migrations.AddField(
            model_name='news',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='news',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='news/'),
        ),
        migrations.AddField(
            model_name='news',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articles', to='news.category'),
        ),
    ]
