from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.http.response import HttpResponse
from storybooks.models import *
from storybooks.serializers import *
from rest_framework import viewsets, permissions, generics, filters, status

def index(request):
    return JsonResponse({ 'message': 'Xygil Backend', 'success': True })

class UserViewSet(viewsets.ModelViewSet):
    """
    User API
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]

class AudioViewSet(viewsets.ModelViewSet):
    """
    Audio API
    """
    queryset = Audio.objects.all()
    serializer_class = AudioSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        data = request.data
        obj = Audio(url=data['url'], title=data['title'])
        obj.save();
        serializer = self.serializer_class(obj)
        return JsonResponse({"audio": serializer.data});

    def list(self, request):
        query = self.queryset.filter(archived=False)
        serializer = self.serializer_class(query, many=True)
        return JsonResponse({"audio": serializer.data})

    def retrieve(self, request, pk):
        query = self.queryset.filter(id=pk)
        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        obj = query.get()
        if obj.archived:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(obj)
        return JsonResponse(serializer.data)

    #Unsafe
    def partial_update(self, request, pk):
        query = self.queryset.filter(id=pk)
        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        obj = query.get()
        print(request.data)
        for key in request.data:
            if hasattr(obj, key):
                setattr(obj, key, request.data[key])
            else:
                return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        obj.save()
        serializer = self.serializer_class(obj)
        return JsonResponse(serializer.data)

    def destroy(self, request, pk):
        query = self.queryset.filter(id=pk)
        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        obj = query.get()
        obj.delete()
        return JsonResponse({}, status=status.HTTP_200_OK)

class LanguageViewSet(viewsets.ModelViewSet):
    """
    Language API
    """
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    # permission_classes = [permissions.IsAuthenticated]
    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        dict = {}
        for entry in serializer.data:
            dict[entry['id']] = entry['name']
        return JsonResponse(dict)

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