from django.db import models
from django.contrib.auth.models import User

class Audio(models.Model):
    url             = models.CharField(max_length=255)
    title           = models.CharField(default="Untitled", max_length=255)
    archived        = models.BooleanField(default=False)

    author          = models.ForeignKey(User, related_name="audio_author", null=True, on_delete=models.SET_NULL)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "audio file"
        verbose_name_plural = "audio files"

class Translation(models.Model):
    title           = models.CharField(default="Untitled Storybook", max_length=255)
    audio           = models.ForeignKey(Audio, on_delete=models.CASCADE)
    published       = models.BooleanField(default=False)

    author          = models.ForeignKey(User, related_name="translation_author", null=True, on_delete=models.SET_NULL)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, related_name="last_updated_by", null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "translation"
        verbose_name_plural = "translations"

class Page(models.Model):
    translation     = models.ForeignKey(Translation, on_delete=models.CASCADE)
    previous_page   = models.ForeignKey("Page", related_name="previous", null=True, on_delete=models.SET_NULL)
    next_page       = models.ForeignKey("Page", related_name="next", null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "page"
        verbose_name_plural = "pages"

class Story(models.Model):
    page            = models.ForeignKey(Page, null=True, on_delete=models.SET_NULL)
    word            = models.CharField(max_length=255)
    index           = models.IntegerField()
    timestamp       = models.DateTimeField()

    class Meta:
        verbose_name = "story"
        verbose_name_plural = "stories"
