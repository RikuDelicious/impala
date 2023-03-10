# Generated by Django 4.1.6 on 2023-02-13 14:48

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Image",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("upload", models.ImageField(max_length=1024, upload_to="images/")),
                ("profile_signiture", models.CharField(max_length=255, unique=True)),
            ],
        ),
    ]
