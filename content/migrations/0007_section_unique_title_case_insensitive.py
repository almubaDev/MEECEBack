# Generated by Django 5.0.1 on 2025-01-26 22:29

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0006_remove_publication_content'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='section',
            constraint=models.UniqueConstraint(fields=('title',), name='unique_title_case_insensitive', violation_error_message='Ya existe una sección con este nombre (sin importar mayúsculas/minúsculas).'),
        ),
    ]
