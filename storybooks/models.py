from django.db import models
from datetime import datetime
#from django.contrib.auth.models import User
import datetime


class Audio(models.Model):
    title = models.CharField(default="Untitled Audio", max_length=255)
    url = models.CharField(max_length=255)
    description = models.CharField(default="Empty", max_length=2048)
    id = models.CharField(primary_key=True, max_length=255)
    archived = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.CharField(max_length=255)
    last_updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.CharField(max_length=255)
    shared_with = models.CharField(default="Not shared with anyone", max_length=2048)
    public = models.BooleanField(default=False)

    class Meta:
        verbose_name = "audio file"
        verbose_name_plural = "audio files"


class Language(models.Model):
    name = models.CharField(max_length=255)
    spaced = models.BooleanField()

    class Meta:
        verbose_name = "language"
        verbose_name_plural = "languages"


class Interpretation(models.Model):
    # id = models.CharField(primary_key=True, max_length=255)
    # public = models.BooleanField(default=False)
    # shared_with = models.JSONField(
    #     default="Not shared with anyone", max_length=2048)  # need special encoder
    # shared_with = models.JSONField(
    #     default="Not shared with anyone", max_length=2048)  # need special encoder
    # audio_id = models.CharField(max_length=255)
    # title = models.CharField(max_length=255)
    # latest_text = models.CharField(max_length=255)
    # archived = models.BooleanField(default=False)
    # language_name = models.CharField(max_length=255)
    # spaced_by = models.CharField(max_length=255)
    # created_by = models.CharField(max_length=255)
    # created_at = models.DateTimeField(auto_now_add=True)
    # last_edited_at = models.DateTimeField(null=True, auto_now=True)
    # last_edited_by = models.CharField(max_length=255)
    # version = models.IntegerField(default=0)

    id              = models.IntegerField(primary_key=True)
    public          = models.BooleanField(default=False)
    shared_editors  = models.ManyToManyField(User)
    shared_viewers  = models.ManyToManyField(User)
    audio_ID        = models.ForeignKey(Audio, on_delete=models.CASCADE)
    title           = models.CharField(max_length=255)
    latest_text     = models.TextField()
    archived        = models.BooleanField(default=False)
    language_name   = models.ForeignKey(Language, on_delete=models.SET_NULL)
    spaced_by       = models.CharField(default='', max_length=255, null=True)
    created_by      = models.ForeignKey(User, on_delete=models.SET_NULL)
    created_at      = models.DateTimeField(default=None, auto_now_add=True)
    last_edited_by  = models.ForeignKey(User, on_delete=models.SET_NULL)
    last_edited_at  = models.DateTimeField(default=None, auto_now=True)
    version         = models.IntegerField(default=1)

    class Meta:
        verbose_name = "interpretation"
        verbose_name_plural = "interpretations"


class Content(models.Model):
    value_index = models.IntegerField()
    audio_id = models.ForeignKey(Audio, on_delete=models.CASCADE)
    interpretation_id = models.ForeignKey(Interpretation, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)
    audio_time = models.TimeField(default=None)
    created_at = models.DateTimeField(default=None, auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(default=None)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "content"
        verbose_name_plural = "contents"


class Interpretation_History(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    interpretation_id = models.CharField(max_length=255)
    public = models.BooleanField(default=False)
    shared_editors = models.CharField(
        default="Not shared with any editors", max_length=2048)  # not sure what to put here
    shared_viewers = models.CharField(
        default="Not shared with any editors", max_length=2048)  # not sure what to put here
    audio_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    latest_text = models.CharField(max_length=255)
    archived = models.BooleanField(default=False)
    language_name = models.CharField(max_length=255)
    spaced_by = models.CharField(max_length=255)
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_edited_at = models.DateTimeField(null=True, auto_now=True)
    last_edited_by = models.CharField(max_length=255)
    version = models.IntegerField(default=0)

    class Meta:
        verbose_name = "interpretation history"
        verbose_name_plural = "interpretation history"


class Translation(models.Model):
    title = models.CharField(default="Untitled Storybook", max_length=255)
    audio_id = models.CharField(max_length=255)
    published = models.BooleanField(default=False)

    language = models.ForeignKey(
        Language, related_name="translation_language", null=True, on_delete=models.SET_NULL)
    author_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.CharField(max_length=255)

    class Meta:
        verbose_name = "translation"
        verbose_name_plural = "translations"


class Story(models.Model):
    translation = models.CharField(max_length=255)
    word = models.CharField(max_length=255)
    index = models.IntegerField()
    timestamp = models.IntegerField(null=True)

    class Meta:
        verbose_name = "story"
        verbose_name_plural = "stories"
