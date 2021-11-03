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

class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story