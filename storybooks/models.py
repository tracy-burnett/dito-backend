from django.db import models
from django.contrib.auth.models import User


class Audio(models.Model):
    url = models.CharField(max_length=255)
    title = models.CharField(default="Untitled Audio", max_length=255)
    description = models.CharField(default="Empty", max_length=2048)
    archived = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(
        User, related_name="last_updated_by", null=True, on_delete=models.SET_NULL)
    uploaded_by = models.ForeignKey(
        User, related_name="uploaded", null=True, on_delete=models.SET_NULL)
    shared_with = models.CharField(default="Not shared with anyone")
    public = models.BooleanField(default=False)

    class Meta:
        verbose_name = "audio file"
        verbose_name_plural = "audio files"


class Audio(models.Model):
    title = models.CharField(default="Untitled Audio", max_length=255)
    url = models.CharField(max_length=255)
    description = models.CharField(default="Empty", max_length=2048)
    id = models.CharField(max_length=255)
    archived = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User, related_name="uploaded", null=True, on_delete=models.SET_NULL)
    last_updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(
        User, related_name="last_updated_by", null=True, on_delete=models.SET_NULL)
    shared_with = models.CharField(default="Not shared with anyone")
    public = models.BooleanField(default=False)

    class Meta:
        verbose_name = "audio file"
        verbose_name_plural = "audio files"


class Interpretation(models.Model):
    id = models.CharField(max_length=255)
    public = models.BooleanField(default=False)
    shared_editors = models.CharField(default="Not shared with any editors")
    shared_viewers = models.CharField(default="Not shared with any editors")
    audio_id = models.ForeignKey(Audio, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    latest_text = models.CharField(max_length=255)
    archived = models.BooleanField(default=False)
    language_name = models.CharField(max_length=255)
    spaced_by = models.ForeignKey(
        User, related_name="uploaded", null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(
        User, related_name="created", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    last_edited_at = models.DateTimeField(null=True, auto_now=True)
    last_edited_by = models.ForeignKey(
        User, related_name="last_edited_by", null=True, on_delete=models.SET_NULL)
    version = models.IntegerField(default=0)

    class Meta:
        verbose_name = "interepretation"
        verbose_name_plural = "interepretations"


class Interpretations_History(models.Model):
    id = models.CharField(max_length=255)
    interpretation_id = models.ForeignKey(Interpretation)
    public = models.BooleanField(default=False)
    shared_editors = models.CharField(default="Not shared with any editors")
    shared_viewers = models.CharField(default="Not shared with any editors")
    audio_id = models.ForeignKey(Audio, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    latest_text = models.CharField(max_length=255)
    archived = models.BooleanField(default=False)
    language_name = models.CharField(max_length=255)
    spaced_by = models.ForeignKey(
        User, related_name="uploaded", null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(
        User, related_name="created", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    last_edited_at = models.DateTimeField(null=True, auto_now=True)
    last_edited_by = models.ForeignKey(
        User, related_name="last_edited_by", null=True, on_delete=models.SET_NULL)
    version = models.IntegerField(default=0)

    class Meta:
        verbose_name = "interepretation history"
        verbose_name_plural = "interepretation history"


class Language(models.Model):
    name = models.CharField(max_length=255)
    spaced = models.BooleanField()

    class Meta:
        verbose_name = "language"
        verbose_name_plural = "languages"


class Translation(models.Model):
    title = models.CharField(default="Untitled Storybook", max_length=255)
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)

    language = models.ForeignKey(
        Language, related_name="translation_language", null=True, on_delete=models.SET_NULL)
    author = models.ForeignKey(
        User, related_name="translation_author", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(
        User, related_name="last_updated_by", null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "translation"
        verbose_name_plural = "translations"


class Story(models.Model):
    translation = models.ForeignKey(
        Translation, on_delete=models.CASCADE, default=0)
    word = models.CharField(max_length=255)
    index = models.IntegerField()
    timestamp = models.IntegerField(null=True)

    class Meta:
        verbose_name = "story"
        verbose_name_plural = "stories"
