from django.db import models
from django.contrib.auth.models import User

class Audio(models.Model):
    url             = models.CharField(max_length=255)
    title           = models.CharField(default="Untitled Audio", max_length=255)
    description     = models.CharField(default="Empty", max_length=2048)
    archived        = models.BooleanField(default=False)

    author          = models.ForeignKey(User, related_name="audio_author", null=True, on_delete=models.SET_NULL)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "audio file"
        verbose_name_plural = "audio files"

class Language(models.Model):
    name            = models.CharField(max_length=255)
    spaced          = models.BooleanField()

    class Meta:
        verbose_name = "language"
        verbose_name_plural = "languages"

class Translation(models.Model):
    title           = models.CharField(default="Untitled Storybook", max_length=255)
    audio           = models.ForeignKey(Audio, on_delete=models.CASCADE)
    published       = models.BooleanField(default=False)

    language        = models.ForeignKey(Language, related_name="translation_language", null=True, on_delete=models.SET_NULL)
    author          = models.ForeignKey(User, related_name="translation_author", null=True, on_delete=models.SET_NULL)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, related_name="last_updated_by", null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "translation"
        verbose_name_plural = "translations"


class Story(models.Model):
    translation     = models.ForeignKey(Translation, on_delete=models.CASCADE, default=0)
    word            = models.CharField(max_length=255)
    index           = models.IntegerField()
    timestamp       = models.IntegerField(null=True)

    class Meta:
        verbose_name = "story"
        verbose_name_plural = "stories"

class Interpretations(models.Model):
    id              = models.IntegerField(primary_key=True)
    public          = models.BooleanField(default=False)
    shared_editors  = models.ManyToManyField(User)
    shared_viewers  = models.ManyToManyField(User)
    audio_ID        = models.ForeignKey(Audio)
    title           = models.CharField(max_length=50)
    latest_text     = models.TextField()
    archived        = models.BooleanField(default=False)
    language_name   = models.ForeignKey(Language)
    spaced_by       = models.CharField(default='', max_length=5, null=True)
    created_by      = models.ForeignKey(User)
    created_at      = models.DateTimeField(default=None, auto_now_add=True)
    last_edited_by  = models.ForeignKey(User)
    last_edited_at  = models.DateTimeField(default=None, auto_now=True)
    version         = models.IntegerField(default=1)

    class Meta:
        verbose_name = "interpretation"
        verbose_name_plural = "interpretations"
