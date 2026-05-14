from django.db import migrations, models


def split_full_name(apps, schema_editor):
    Student = apps.get_model("students", "Student")

    for student in Student.objects.all():
        parts = student.full_name.strip().split(maxsplit=1)
        student.last_name = parts[0] if parts else ""
        student.other_names = parts[1] if len(parts) > 1 else ""
        student.save(update_fields=["last_name", "other_names"])


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0006_alter_student_gender"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="last_name",
            field=models.CharField(
                default="",
                help_text="Student surname or family name",
                max_length=100,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="student",
            name="other_names",
            field=models.CharField(
                blank=True,
                help_text="Student first name and other names",
                max_length=150,
            ),
        ),
        migrations.AddField(
            model_name="student",
            name="cgpa",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Cumulative grade point average",
                max_digits=4,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="student",
            name="grade",
            field=models.CharField(
                blank=True,
                help_text="Final grade or classification",
                max_length=50,
            ),
        ),
        migrations.RunPython(split_full_name, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="student",
            name="full_name",
        ),
        migrations.AlterModelOptions(
            name="student",
            options={"ordering": ["last_name", "other_names"]},
        ),
    ]
