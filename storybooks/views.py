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
            return HttpResponse(status=404)
        obj = query.get()
        obj.delete()
        return HttpResponse(status=200)

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
    #Unsafe (can be overridden)
    def create(self, request, aid, lid):
        query = Audio.objects.all().filter(id=aid)
        if not query:
            return HttpResponse(status=404)
        audio = query.get()
        
        query = Language.objects.all().filter(id=lid)
        if not query:
            return HttpResponse(status=404)
        language = query.get()

        #Check unique
        if self.queryset.filter(audio_id=aid, language_id=lid):
            return HttpResponse(status=400)

        data = request.data
        translation = Translation(title=data['title'], audio=audio, language=language)
        
        text_array = []
        if language.spaced:
            text_array = data['text'].split(" ")
        else:
            text_array = list(data['text'])

        words = []
        for i in range(len(text_array)):
            word = text_array[i]
            words.append(Story(translation=translation, word=word, index=i))
        
        translation.save()
        Story.objects.bulk_create(words)
        return HttpResponse(status=200)

    def retrieve(self, request, aid, lid):
        translation = self.queryset.get(audio_id=aid, language_id=lid)
        if not translation:
            return HttpResponse(status=404)
        #if not translation.published:
        #    return HttpResponse(status=400)

        query = Story.objects.all().filter(translation=translation).order_by('index')
        serializer = StorySerializer(query, many=True)
        words = [entry['word'] for entry in serializer.data]
        text = ""
        if translation.language.spaced:
            text = ' '.join(words)
        else:
            text = "".join(words)
        return JsonResponse({"text": text})

    def destroy(self, request, aid, lid):
        query = self.queryset.filter(audio_id=aid).filter(language_id=lid)
        if not query:
            return HttpResponse(status=404)
        query.get().delete()
        return HttpResponse(status=200)
    
    def list_languages(self, request, aid):
        query = self.queryset.filter(audio_id=aid).order_by('language')
        if not query:
            return HttpResponse(status=404)
        serializer = self.serializer_class(query, many=True)
        languages = [entry.language.id for entry in query]
        return JsonResponse({"languages": languages})


    #Update helper function - finds the closest difference between a and b
    #Returns: a list with integers and tuples
    #If the value is an integer, remove the character with that original index from a
    #If the value is a tuple (i, v), insert v to that original index from a 
    def closest(self, a, b):
        memo = {}
        self.closest_helper(a, b, 0, 0, memo)
        return self.trace(a, b, 0, 0, memo)

    def closest_helper(self, a, b, a_index, b_index, memo):
        if a_index >= len(a) or b_index >= len(b):
            return 0
        
        if not (a_index, b_index) in memo:
            if a[a_index] == b[b_index]:
                memo[(a_index, b_index)] = 1 + self.closest_helper(a, b, a_index + 1, b_index + 1, memo)
            else:
                memo[(a_index, b_index)] = max(self.closest_helper(a, b, a_index + 1, b_index, memo), self.closest_helper(a, b, a_index, b_index + 1, memo))
        
        return memo[(a_index, b_index)]

    def trace(self, a, b, a_index, b_index, memo):
        path = []
        while a_index < len(a) and b_index < len(b):
            if a[a_index] == b[b_index]:
                a_index += 1
                b_index += 1
            else:
                if a_index + 1 >= len(a):
                    path.append((a_index, b[b_index]))
                    b_index += 1
                elif b_index + 1 >= len(b):
                    path.append(a_index)
                    a_index += 1
                elif memo[(a_index + 1, b_index)] < memo[(a_index, b_index + 1)]:
                    path.append((a_index, b[b_index]))
                    b_index += 1
                else:
                    path.append(a_index)
                    a_index += 1

        if a_index >= len(a):
            for index in range(b_index, len(b)):
                path.append((a_index, b[index]))
        elif b_index >= len(b):
            for index in range(a_index, len(a)):
                path.append(index)
        
        return path

    def update(self, request, aid, lid):
        translation = self.queryset.get(audio_id=aid, language_id=lid)
        if not translation:
            return HttpResponse(status=404)

        query = Language.objects.all().filter(id=lid)
        if not query:
            return HttpResponse(status=404)
        language = query.get()

        query = Story.objects.all().filter(translation=translation).order_by('index')
        serializer = StorySerializer(query, many=True)
        a = [entry['word'] for entry in serializer.data]
        b = []
        if language.spaced:
            b = request.data['text'].split(" ")
        else:
            b = list(request.data['text'])
        add = []
        subtract = []
        changed = []
        delta = 0
        path = self.closest(a, b)
        #print("path:", path)
        path_index = 0
        
        def traverse_path(i):
            nonlocal path_index
            nonlocal delta
            while path_index < len(path):
                if isinstance(path[path_index], int):
                    if path[path_index] == i:
                        subtract.append(query[i])
                        delta -= 1
                        path_index += 1
                    else:
                        break
                else:
                    if path[path_index][0] == i:
                        add.append(Story(translation=translation, word=path[path_index][1], index=i + delta))
                        delta += 1
                        path_index += 1
                    else:
                        break
        
        for i in range(len(query)):
            traverse_path(i)
            if (delta != 0):
                query[i].index += delta
                changed.append(query[i])
        traverse_path(len(query))

        Story.objects.bulk_update(changed, ['index'])
        Story.objects.bulk_create(add)
        for obj in subtract:
            obj.delete()

        return HttpResponse(status=200)

class StoryViewSet(viewsets.ModelViewSet):
    """
    Story API
    """
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    # permission_classes = [permissions.IsAuthenticated]