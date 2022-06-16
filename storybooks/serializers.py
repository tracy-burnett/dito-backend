from django.contrib.auth.models import User
from storybooks.models import *
from rest_framework import serializers
from storybooks.s3 import *



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class ExtendedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extended_User
        fields = ['user_ID', 'display_name', 'description', 'anonymous', 'created_at', 'email']

class AudioSerializer(serializers.ModelSerializer):
    uploaded_by = ExtendedUserSerializer(read_only=True) # FOR DEMONSTRATION
    shared_editors = ExtendedUserSerializer(read_only=True, many=True) # FOR DEMONSTRATION
    shared_viewers = ExtendedUserSerializer(read_only=True, many=True) # FOR DEMONSTRATION
    # last_updated_by = ExtendedUserSerializer(read_only=True) # FOR DEMONSTRATION

    class Meta:
        model = Audio
        fields = ['id', 'url', 'title', 'description','archived','uploaded_at','uploaded_by','last_updated_at','last_updated_by','shared_editors','shared_viewers','public']

class InterpretationSerializer(serializers.ModelSerializer):
    created_by = ExtendedUserSerializer(read_only=True) # FOR DEMONSTRATION
    shared_editors = ExtendedUserSerializer(read_only=True, many=True) # FOR DEMONSTRATION
    shared_viewers = ExtendedUserSerializer(read_only=True, many=True) # FOR DEMONSTRATION

    class Meta:
        model = Interpretation
        fields = ['id','title', 'public','shared_editors','shared_viewers','audio_ID','latest_text','archived','language_name','spaced_by','created_by','created_at','last_edited_at','last_edited_by','version']

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

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['value_index', 'audio_id', 'interpretation_id', 'value', 'audio_time', 'created_at', 'created_by', 'updated_at', 'updated_by']