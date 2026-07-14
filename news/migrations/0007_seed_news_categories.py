from django.db import migrations
from django.utils.text import slugify


def build_unique_slug(base_slug, existing_slugs):
    slug = base_slug or "category"
    counter = 1
    while slug in existing_slugs:
        slug = f"{base_slug}-{counter}" if base_slug else f"category-{counter}"
        counter += 1
    existing_slugs.add(slug)
    return slug


def seed_categories(apps, schema_editor):
    Category = apps.get_model("news", "Category")

    category_names = [
        "Institutional News",
        "College News",
        "Announcements",
        "Admissions",
        "Academic Calendar",
        "Events",
        "Convocation",
        "Matriculation",
        "Accreditation",
        "Partnerships & Collaborations",
        "Circulars",
        "Press Releases",
        "Academic Publications",
        "Original Research",
        "Review Articles",
        "Case Studies",
        "Short Communications",
        "Editorials",
        "Perspectives",
        "Technical Notes",
        "Commentaries",
        "Letters to the Editor",
        "Public Health",
        "Epidemiology",
        "Health Promotion",
        "Environmental Health",
        "Occupational Health",
        "Health Policy",
        "Disease Prevention",
        "Global Health",
        "Community Health",
        "Clinical Sciences",
        "Nursing Sciences",
        "Midwifery",
        "Medical Laboratory Science",
        "Pharmacy Technology",
        "Radiography",
        "Clinical Practice",
        "Patient Care",
        "Health Sciences Education",
        "Medical Education",
        "Curriculum Development",
        "Teaching & Learning",
        "E-Learning",
        "Educational Technology",
        "Student Research",
        "Technology & Innovation",
        "Health Informatics",
        "Digital Health",
        "Artificial Intelligence",
        "Machine Learning",
        "Data Science",
        "Health Information Management",
        "Telemedicine",
        "Biomedical Technology",
        "Policy & Governance",
        "Institutional Governance",
        "Quality Assurance",
        "Leadership",
        "Strategic Planning",
        "Healthcare Management",
        "Student Corner",
        "Student Research",
        "Student Projects",
        "Student Publications",
        "Student Activities",
        "Alumni Stories",
        "Career Development",
    ]

    category_names = list(dict.fromkeys(category_names))

    existing_slugs = set(
        Category.objects.exclude(slug="").values_list("slug", flat=True)
    )
    existing_names = set(Category.objects.values_list("name", flat=True))

    # Backfill any legacy rows that still have blank slugs from older imports.
    for category in Category.objects.filter(slug=""):
        category.slug = build_unique_slug(slugify(category.name), existing_slugs)
        category.save(update_fields=["slug"])

    for name in category_names:
        if name in existing_names:
            continue

        Category.objects.create(
            name=name,
            slug=build_unique_slug(slugify(name), existing_slugs),
        )


def unseed_categories(apps, schema_editor):
    Category = apps.get_model("news", "Category")

    category_names = [
        "Institutional News",
        "College News",
        "Announcements",
        "Admissions",
        "Academic Calendar",
        "Events",
        "Convocation",
        "Matriculation",
        "Accreditation",
        "Partnerships & Collaborations",
        "Circulars",
        "Press Releases",
        "Academic Publications",
        "Original Research",
        "Review Articles",
        "Case Studies",
        "Short Communications",
        "Editorials",
        "Perspectives",
        "Technical Notes",
        "Commentaries",
        "Letters to the Editor",
        "Public Health",
        "Epidemiology",
        "Health Promotion",
        "Environmental Health",
        "Occupational Health",
        "Health Policy",
        "Disease Prevention",
        "Global Health",
        "Community Health",
        "Clinical Sciences",
        "Nursing Sciences",
        "Midwifery",
        "Medical Laboratory Science",
        "Pharmacy Technology",
        "Radiography",
        "Clinical Practice",
        "Patient Care",
        "Health Sciences Education",
        "Medical Education",
        "Curriculum Development",
        "Teaching & Learning",
        "E-Learning",
        "Educational Technology",
        "Student Research",
        "Technology & Innovation",
        "Health Informatics",
        "Digital Health",
        "Artificial Intelligence",
        "Machine Learning",
        "Data Science",
        "Health Information Management",
        "Telemedicine",
        "Biomedical Technology",
        "Policy & Governance",
        "Institutional Governance",
        "Quality Assurance",
        "Leadership",
        "Strategic Planning",
        "Healthcare Management",
        "Student Corner",
        "Student Projects",
        "Student Publications",
        "Student Activities",
        "Alumni Stories",
        "Career Development",
    ]

    category_names = list(dict.fromkeys(category_names))

    Category.objects.filter(name__in=category_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0006_comment"),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
