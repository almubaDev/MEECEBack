# Generated by Django 5.0.1 on 2025-01-10 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_remove_block_created_by_remove_block_publication_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='content',
        ),
        migrations.AddField(
            model_name='publication',
            name='layout',
            field=models.JSONField(default=list),
        ),
    ]
