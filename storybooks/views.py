from django.http import JsonResponse
from django.contrib.auth.models import User
from storybooks.models import *
from storybooks.serializers import *
from rest_framework import viewsets, permissions, generics, filters

def index(request):
    return JsonResponse({ 'message': 'Xygil Backend', 'success': True })

class UserViewSet(viewsets.ModelViewSet):
    """
    User API
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]

class AudioListView(generics.ListAPIView):
    """
    Audio API
    """
    queryset = Audio.objects.all()
    serializer_class = AudioSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'translations__title', 'audio_author', 'translations__translation_author']

class TranslationViewSet(viewsets.ModelViewSet):
    """
    Translation API
    """
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer
    # permission_classes = [permissions.IsAuthenticated]

class StoryViewSet(viewsets.ModelViewSet):
    """
    Story API
    """
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    # permission_classes = [permissions.IsAuthenticated]