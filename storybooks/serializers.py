from django.contrib.auth.models import User
from storybooks.models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = ['id', 'url', 'title', 'description','archived','uploaded_at','uploaded_by','last_updated_at','last_updated_by','shared_with','public']

class InterpretationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interpretation
        fields = ['id','public','shared_editors','shared_viewers','audio_id','latest_text','archived','language_name','spaced_by','created_by','created_at','last_edited_at','last_edited_by','version']

class InterpretationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Interpretation_History
        fields = ['id','interpretation_id','public','shared_editors','shared_viewers','audio_id','title','latest_text','archived','language_name','spaced_by','created_by','created_at','last_edited_at','last_edited_by','version']

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name']

class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = ['title', 'audio', 'published', 'language', 'author']

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['word', 'index', 'timestamp']