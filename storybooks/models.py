from django.db import models


class Language(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    bAdjust = models.CharField(max_length=255, default="Adjust")
    bClose = models.CharField(max_length=255, default="Close")
    bInterpretation = models.CharField(max_length=255, default="Interpretation")
    bViewing = models.CharField(max_length=255, default="Viewing")
    bDownload = models.CharField(max_length=255, default="Download")
    bScribing = models.CharField(max_length=255, default="Scribing")
    bEditing = models.CharField(max_length=255, default="Editing")
    bRefining = models.CharField(max_length=255, default="Refining")
    bStudying = models.CharField(max_length=255, default="Studying")
    bResetSensitivity = models.CharField(max_length=255, default="Reset Sensitivity")
    bNewPrompt = models.CharField(max_length=255, default="New Prompt")
    bClearNew = models.CharField(max_length=255, default="Clear New")
    bNewPhrase = models.CharField(max_length=255, default="New Phrase")
    sPlaybackSpeed = models.CharField(max_length=255, default="playback speed")
    sZoom = models.CharField(max_length=255, default="zoom")
    sChangeFontSize = models.CharField(max_length=255, default="change font size")
    sScribeLessMore = models.CharField(max_length=255, default="scribe less / more")
    sHighlightLessMore = models.CharField(max_length=255, default="highlight less / more")
    sPhraseLength = models.CharField(max_length=255, default="phrase length")
    cClearSelection = models.CharField(max_length=255, default="Clear Selection")
    cRepeatOnOff = models.CharField(max_length=255, default="Repeat On / Off")
    cAutoscrollOnOff = models.CharField(max_length=255, default="Autoscroll On / Off")
    oCreateNewInterpretation = models.CharField(max_length=255, default="Create New Interpretation")
    oUploadInterpretationFile = models.CharField(max_length=255, default="Upload Inter-pretation File")
    oAddAnotherConsole = models.CharField(max_length=255, default="Add Another Console")

class Extended_User(models.Model):
    # The default for Django Models CharField is 255, which should be enough for both user_ID and display_name
    email = models.CharField(max_length=255)
    user_ID = models.CharField(max_length=255, primary_key=True)
    display_name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) # basically adds the timestamp when the record is added
    anonymous = models.BooleanField(default=False)

class Audio(models.Model):
    title = models.CharField(default="Untitled Audio", max_length=255)
    url = models.CharField(max_length=255) # originally for the cover image, now purposed to the home base web URL
    description = models.CharField(default="Empty", max_length=2048)
    id = models.CharField(primary_key=True, max_length=255)
    archived = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(Extended_User, related_name="audio_uploaded_by", null=True, on_delete=models.SET_NULL) # FOR DEMONSTRATION
    last_updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(Extended_User, related_name="audio_last_updated_by", null=True, on_delete=models.SET_NULL)
    shared_editors = models.ManyToManyField(Extended_User, related_name="audio_shared_editors", blank=True)
    shared_viewers = models.ManyToManyField(Extended_User, related_name="audio_shared_viewers", blank=True)
    public = models.BooleanField(default=False)
    peaks=models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "audio file"
        verbose_name_plural = "audio files"

class Interpretation(models.Model):

    id              = models.CharField(primary_key=True, max_length=255)
    public          = models.BooleanField(default=False)
    shared_editors  = models.ManyToManyField(Extended_User,related_name="interpretation_shared_editors", blank=True)
    shared_viewers  = models.ManyToManyField(Extended_User,related_name="interpretation_shared_viewers", blank=True)
    audio_ID        = models.ForeignKey(Audio, related_name="interpretation_audio_ID", null=True, on_delete=models.SET_NULL)
    title           = models.CharField(max_length=255)
    latest_text     = models.TextField(null=True)
    archived        = models.BooleanField(default=False)
    language_name   = models.CharField(max_length=255)
    spaced_by       = models.CharField(max_length=1, null=True)
    created_by      = models.ForeignKey(Extended_User, related_name="interpretation_created_by", null=True, on_delete=models.SET_NULL)
    created_at      = models.DateTimeField(auto_now_add=True)
    last_edited_by  = models.ForeignKey(Extended_User, related_name="interpretation_last_edited_by", null=True, on_delete=models.SET_NULL)
    last_edited_at  = models.DateTimeField(auto_now=True)
    version         = models.IntegerField(default=1)


    def __str__(self):
        return f"{self.id} {self.title} {self.language_name}"

    class Meta:
        verbose_name = "interpretation"
        verbose_name_plural = "interpretations"


class Content(models.Model):
    value_index = models.IntegerField()
    audio_id = models.ForeignKey(Audio, related_name="content_audio_id", null=True, on_delete=models.SET_NULL)
    interpretation_id = models.ForeignKey(Interpretation, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)
    audio_time = models.IntegerField(null=True)
    audio_offset = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Extended_User, related_name="content_created_by", null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(Extended_User, related_name="content_updated_by", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.interpretation_id} {self.value} {self.value_index} {self.audio_time} {self.audio_offset}"

    class Meta:
        verbose_name = "content"
        verbose_name_plural = "contents"


class Interpretation_History(models.Model):
    interpretation_ID = models.CharField(max_length=255)
    public          = models.BooleanField(default=False)
    shared_editors  = models.ManyToManyField(Extended_User,related_name="interpretation_history_shared_editors", blank=True)
    shared_viewers  = models.ManyToManyField(Extended_User,related_name="interpretation_history_shared_viewers", blank=True)
    audio_ID        = models.ForeignKey(Audio, related_name="interpretation_history_audio_ID", null=True, on_delete=models.SET_NULL)
    title           = models.CharField(max_length=255)
    latest_text     = models.TextField(null=True)
    archived        = models.BooleanField(default=False)
    language_name   = models.CharField(max_length=255)
    spaced_by       = models.CharField(max_length=1, null=True)
    created_by      = models.ForeignKey(Extended_User, related_name="interpretation_history_created_by", null=True, on_delete=models.SET_NULL)
    created_at      = models.DateTimeField()
    last_edited_by  = models.ForeignKey(Extended_User, related_name="interpretation_history_last_edited_by", null=True, on_delete=models.SET_NULL)
    last_edited_at  = models.DateTimeField()
    version         = models.IntegerField()

    class Meta:
        verbose_name = "interpretation history"
        verbose_name_plural = "interpretation history"





