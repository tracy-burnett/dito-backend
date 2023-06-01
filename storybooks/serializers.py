from django.contrib.auth.models import User
from storybooks.models import *
from rest_framework import serializers
from storybooks.s3 import *


class ExtendedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extended_User
        fields = ['user_ID', 'display_name', 'description', 'anonymous', 'created_at', 'email']

class ExtendedUserSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Extended_User
        fields = ['user_ID', 'display_name']

class ExtendedUserSerializer3(serializers.ModelSerializer):
    class Meta:
        model = Extended_User
        fields = []

class AudioSerializer(serializers.ModelSerializer):
    uploaded_by = ExtendedUserSerializer2(read_only=True)
    shared_editors = ExtendedUserSerializer2(read_only=True, many=True) 
    shared_viewers = ExtendedUserSerializer2(read_only=True, many=True) 

    class Meta:
        model = Audio
        fields = ['id', 'url', 'title', 'description','archived','uploaded_at','uploaded_by','last_updated_at','last_updated_by','shared_editors','shared_viewers','public','peaks']

class AudioSerializer2(serializers.ModelSerializer):
    uploaded_by = ExtendedUserSerializer2(read_only=True) 
    shared_editors = ExtendedUserSerializer2(read_only=True, many=True) 
    shared_viewers = ExtendedUserSerializer2(read_only=True, many=True) 

    class Meta:
        model = Audio
        fields = ['id', 'url', 'title', 'description','archived','uploaded_at','uploaded_by','last_updated_at','last_updated_by','shared_editors','shared_viewers','public']

class AudioSerializer3(serializers.ModelSerializer):
    uploaded_by = ExtendedUserSerializer2(read_only=True) 
    shared_editors = ExtendedUserSerializer3(read_only=True, many=True)
    shared_viewers = ExtendedUserSerializer2(read_only=True, many=True) 

    class Meta:
        model = Audio
        fields = ['id', 'url', 'title', 'description','archived','uploaded_at','uploaded_by','last_updated_at','last_updated_by','shared_editors','shared_viewers','public']


class AudioSerializerPublic(serializers.ModelSerializer):
    uploaded_by = ExtendedUserSerializer2(read_only=True)

    class Meta:
        model = Audio
        fields = ['id', 'url', 'title', 'description','archived','uploaded_at','uploaded_by','last_updated_at','last_updated_by','public']

class InterpretationSerializer(serializers.ModelSerializer):
    created_by = ExtendedUserSerializer2(read_only=True)
    shared_editors = ExtendedUserSerializer2(read_only=True, many=True) 
    shared_viewers = ExtendedUserSerializer2(read_only=True, many=True) 

    class Meta:
        model = Interpretation
        fields = ['id','title', 'public','shared_editors','shared_viewers','audio_ID','latest_text','archived','language_name','spaced_by','created_by','created_at','last_edited_at','last_edited_by','version']

class InterpretationSerializerBrief(serializers.ModelSerializer):

    class Meta:
        model = Interpretation
        fields = ['title','latest_text','language_name','spaced_by','audio_ID']

class InterpretationSerializer2(serializers.ModelSerializer):
    created_by = ExtendedUserSerializer2(read_only=True) 
    shared_editors = ExtendedUserSerializer3(read_only=True, many=True) 
    shared_viewers = ExtendedUserSerializer2(read_only=True, many=True) 

    class Meta:
        model = Interpretation
        fields = ['id','title', 'public','shared_editors','shared_viewers','audio_ID','latest_text','archived','language_name','spaced_by','created_by','created_at','last_edited_at','last_edited_by','version']

class InterpretationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Interpretation_History
        fields = ['id','interpretation_id','public','shared_editors','shared_viewers','audio_id','title','latest_text','archived','language_name','spaced_by','created_by','created_at','last_edited_at','last_edited_by','version']

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['value_index', 'audio_id', 'interpretation_id', 'value', 'audio_time', 'created_at', 'created_by', 'updated_at', 'updated_by']