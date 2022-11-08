# Generated by Django 4.0.5 on 2022-11-08 19:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Audio',
            fields=[
                ('title', models.CharField(default='Untitled Audio', max_length=255)),
                ('url', models.CharField(max_length=255)),
                ('description', models.CharField(default='Empty', max_length=2048)),
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('archived', models.BooleanField(default=False)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
                ('public', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'audio file',
                'verbose_name_plural': 'audio files',
            },
        ),
        migrations.CreateModel(
            name='Extended_User',
            fields=[
                ('email', models.CharField(max_length=255)),
                ('user_ID', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('display_name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('anonymous', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('spaced', models.BooleanField()),
            ],
            options={
                'verbose_name': 'language',
                'verbose_name_plural': 'languages',
            },
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('title', models.CharField(default='Untitled Storybook', max_length=255)),
                ('audio_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('published', models.BooleanField(default=False)),
                ('text', models.TextField(null=True)),
                ('author_id', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_updated_by', models.CharField(max_length=255)),
                ('language', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='translation_language', to='storybooks.language')),
            ],
            options={
                'verbose_name': 'translation',
                'verbose_name_plural': 'translations',
            },
        ),
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=255)),
                ('index', models.IntegerField()),
                ('timestamp', models.IntegerField(null=True)),
                ('translation', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='storybooks.translation')),
            ],
            options={
                'verbose_name': 'story',
                'verbose_name_plural': 'stories',
            },
        ),
        migrations.CreateModel(
            name='Interpretation_History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interpretation_ID', models.CharField(max_length=255)),
                ('public', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=255)),
                ('latest_text', models.TextField(null=True)),
                ('archived', models.BooleanField(default=False)),
                ('language_name', models.CharField(max_length=255)),
                ('spaced_by', models.CharField(max_length=1, null=True)),
                ('created_at', models.DateTimeField()),
                ('last_edited_at', models.DateTimeField()),
                ('version', models.IntegerField()),
                ('audio_ID', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interpretation_history_audio_ID', to='storybooks.audio')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interpretation_history_created_by', to='storybooks.extended_user')),
                ('last_edited_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interpretation_history_last_edited_by', to='storybooks.extended_user')),
                ('shared_editors', models.ManyToManyField(blank=True, related_name='interpretation_history_shared_editors', to='storybooks.extended_user')),
                ('shared_viewers', models.ManyToManyField(blank=True, related_name='interpretation_history_shared_viewers', to='storybooks.extended_user')),
            ],
            options={
                'verbose_name': 'interpretation history',
                'verbose_name_plural': 'interpretation history',
            },
        ),
        migrations.CreateModel(
            name='Interpretation',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('public', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=255)),
                ('latest_text', models.TextField(null=True)),
                ('archived', models.BooleanField(default=False)),
                ('language_name', models.CharField(max_length=255)),
                ('spaced_by', models.CharField(max_length=1, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_edited_at', models.DateTimeField(auto_now=True)),
                ('version', models.IntegerField(default=1)),
                ('audio_ID', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interpretation_audio_ID', to='storybooks.audio')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interpretation_created_by', to='storybooks.extended_user')),
                ('last_edited_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interpretation_last_edited_by', to='storybooks.extended_user')),
                ('shared_editors', models.ManyToManyField(blank=True, related_name='interpretation_shared_editors', to='storybooks.extended_user')),
                ('shared_viewers', models.ManyToManyField(blank=True, related_name='interpretation_shared_viewers', to='storybooks.extended_user')),
            ],
            options={
                'verbose_name': 'interpretation',
                'verbose_name_plural': 'interpretations',
            },
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value_index', models.IntegerField()),
                ('value', models.CharField(max_length=255)),
                ('audio_time', models.IntegerField(null=True)),
                ('audio_offset', models.IntegerField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('audio_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='content_audio_id', to='storybooks.audio')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='content_created_by', to='storybooks.extended_user')),
                ('interpretation_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='storybooks.interpretation')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='content_updated_by', to='storybooks.extended_user')),
            ],
            options={
                'verbose_name': 'content',
                'verbose_name_plural': 'contents',
            },
        ),
        migrations.AddField(
            model_name='audio',
            name='last_updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audio_last_updated_by', to='storybooks.extended_user'),
        ),
        migrations.AddField(
            model_name='audio',
            name='shared_editors',
            field=models.ManyToManyField(blank=True, related_name='audio_shared_editors', to='storybooks.extended_user'),
        ),
        migrations.AddField(
            model_name='audio',
            name='shared_viewers',
            field=models.ManyToManyField(blank=True, related_name='audio_shared_viewers', to='storybooks.extended_user'),
        ),
        migrations.AddField(
            model_name='audio',
            name='uploaded_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audio_uploaded_by', to='storybooks.extended_user'),
        ),
    ]
