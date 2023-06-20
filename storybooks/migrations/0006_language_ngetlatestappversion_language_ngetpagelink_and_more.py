# Generated by Django 4.0.5 on 2023-06-20 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storybooks', '0005_remove_language_cautoscrollonoff_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='nGetLatestAppVersion',
            field=models.CharField(default='Get Latest App Version', max_length=255),
        ),
        migrations.AddField(
            model_name='language',
            name='nGetPageLink',
            field=models.CharField(default='Get Page Link', max_length=255),
        ),
        migrations.AddField(
            model_name='language',
            name='nLogin',
            field=models.CharField(default='Login', max_length=255),
        ),
        migrations.AddField(
            model_name='language',
            name='nLogout',
            field=models.CharField(default='Logout', max_length=255),
        ),
    ]
