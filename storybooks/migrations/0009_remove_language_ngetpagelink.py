# Generated by Django 4.0.5 on 2023-06-21 18:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storybooks', '0008_language_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='language',
            name='nGetPageLink',
        ),
    ]
