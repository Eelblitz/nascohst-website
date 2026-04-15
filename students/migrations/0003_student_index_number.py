from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_student_gender_student_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='index_number',
            field=models.CharField(default='', help_text='Student index number', max_length=50),
            preserve_default=False,
        ),
    ]
