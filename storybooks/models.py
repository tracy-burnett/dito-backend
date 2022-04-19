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



# A more accurate account of what the Audio model should look like below
 
# class Audio(models.Model):
#     title = models.CharField(default="Untitled Audio", max_length=255)
#     url = models.CharField(max_length=255)
#     description = models.CharField(default="Empty", max_length=2048)
#     id = models.CharField(primary_key=True, max_length=255)
#     archived = models.BooleanField(default=False)
#     uploaded_at = models.DateTimeField(auto_now_add=True) # should be changed to extended user tables
#     uploaded_by = models.ForeignKey(User, related_name="audio_uploaded_by", null=True, on_delete=models.SET_NULL)
#     last_updated_at = models.DateTimeField(auto_now=True) # should be changed to extended user tables
#     last_updated_by = models.ForeignKey(User, related_name="audio_last_updated_by", null=True,on_delete=models.SET_NULL) # should be changed to extended user tables
#     shared_with = models.ManyToManyField(User)
#     public = models.BooleanField(default=False)



#     class Meta:
#         verbose_name = "audio file"
#         verbose_name_plural = "audio files"


# class Interpretations(models.Model):
#     id = models.IntegerField(primary_key=True)
#     public = models.BooleanField(default=False)
#     shared_editors = models.ManyToManyField(User)
#     shared_viewers = models.ManyToManyField(User)
#     audio_ID = models.ForeignKey(Audio,null=True,on_delete=models.SET_NULL)
#     title = models.CharField(max_length=50)
#     latest_text = models.TextField()
#     archived = models.BooleanField(default=False)
#     language_name = models.CharField(default='', max_length=246, null=True)
#     spaced_by = models.CharField(default='', max_length=5, null=True) # should be changed to extended user tables
#     created_by = models.ForeignKey(User, on_delete=models.SET_NULL)
#     created_at = models.DateTimeField(auto_now_add=True)  # should be changed to extended user tables
#     last_edited_by = models.ForeignKey(User, on_delete=models.SET_NULL)
#     last_edited_at = models.DateTimeField(default=None, auto_now=True)
#     version = models.IntegerField(default=1)

#     class Meta:
#         verbose_name = "interpretation"
#         verbose_name_plural = "interpretations"


class Language(models.Model):
    name = models.CharField(max_length=255)
    spaced = models.BooleanField()

    class Meta:
        verbose_name = "language"
        verbose_name_plural = "languages"


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
