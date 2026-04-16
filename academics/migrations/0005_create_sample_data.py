from django.db import migrations


def create_sample_data(apps, schema_editor):
    School = apps.get_model('academics', 'School')
    Programme = apps.get_model('academics', 'Programme')

    # Create sample school
    school = School.objects.create(
        name='School of Health Sciences',
        description='School offering health science programmes'
    )

    # Create sample programmes
    programmes = [
        ('Nursing Science', 'ND', 'Nursing programme'),
        ('Medical Laboratory Science', 'ND', 'Medical lab programme'),
        ('Public Health', 'ND', 'Public health programme'),
    ]

    for name, level, desc in programmes:
        Programme.objects.create(
            name=name,
            level=level,
            school=school,
            description=desc
        )


def reverse_sample_data(apps, schema_editor):
    School = apps.get_model('academics', 'School')
    Programme = apps.get_model('academics', 'Programme')

    # Delete sample programmes
    Programme.objects.filter(school__name='School of Health Sciences').delete()

    # Delete sample school
    School.objects.filter(name='School of Health Sciences').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0004_alter_programme_career_prospects_and_more'),
    ]

    operations = [
        migrations.RunPython(create_sample_data, reverse_sample_data),
    ]