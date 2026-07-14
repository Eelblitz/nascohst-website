from django.db import migrations


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

    # Backfill any legacy rows that still have blank slugs from older imports.
    for category in Category.objects.filter(slug=""):
        category.save()

    for name in category_names:
        category, created = Category.objects.get_or_create(name=name)
        if created or not category.slug:
            category.save()


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
