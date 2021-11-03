from django.db import models
from django.contrib.auth.models import User

class Audio(models.Model):
    url             = models.CharField(max_length=255)
    title           = models.CharField(default="Untitled", max_length=255)
    archived        = models.BooleanField(default=False)

    createdAt       = models.DateTimeField(auto_now_add=True)
    updatedAt       = models.DateTimeField(auto_now=True)
    lastUpdatedBy   = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "audio file"
        verbose_name_plural = "audio files"

class Translation(models.Model):
    title           = models.CharField(default="Untitled Storybook", max_length=255)
    audio           = models.ForeignKey(Audio, on_delete=models.CASCADE)
    published       = models.BooleanField(default=False)

    author          = models.ForeignKey(User, related_name="author", null=True, on_delete=models.SET_NULL)
    createdAt       = models.DateTimeField(auto_now_add=True)
    updatedAt       = models.DateTimeField(auto_now=True)
    lastUpdatedBy   = models.ForeignKey(User, related_name="lastUpdatedBy", null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "translation"
        verbose_name_plural = "translations"

class Story(models.Model):
    translation     = models.ForeignKey(Translation, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "story"
        verbose_name_plural = "stories"
