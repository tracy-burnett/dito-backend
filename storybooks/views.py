from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.http.response import HttpResponse
from storybooks.models import *
from storybooks.s3 import *
from storybooks.serializers import *
from rest_framework import views, viewsets, permissions, generics, filters, status
from rest_framework.response import Response
from bisect import bisect_left
import ast
import secrets


# def index(request):
#     return JsonResponse({ 'message': 'Xygil Backend', 'success': True })
# this doesn't work


# If somebody visits /s3/ they will receive an upload URL and a new hashed audio ID that will apply to whatever audio they upload to that URL.
# If somebody posts an audio_ID to /s3/ they will receive a URL to download the audio file with that ID.
class UploadFileViewSet(viewsets.ViewSet):
    def presignedposturl(self, request, pk=None):
        ext = request.data['ext']
        audio_ID = secrets.token_urlsafe(8) + ext
        url = S3().get_presigned_url(audio_ID)

        return Response({'url': url, 'audio_ID': audio_ID})


class DownloadFileViewSet(viewsets.ViewSet):
    def presignedgeturl(self, request, pk=None):
        audio_ID = request.data['audio_ID']
        url = S3().get_file(audio_ID)

        return Response({'url': url, 'audio_ID': audio_ID})


class UserViewSet(viewsets.ModelViewSet):
    """
    User API
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]

#AudioViewSet class is accessed at /api/audio
class AudioViewSet(viewsets.ModelViewSet):
    """
    Audio API
    """
    queryset = Audio.objects.all()
    serializer_class = AudioSerializer
    permission_classes = [permissions.AllowAny] # this overrides project-level permission in settings.py

# presumably, somebody posts two fields, url and title, to the URL, then it creates a new audio object in the database.
    def create(self, request):
        data = request.data
        obj = Audio(url=data['url'], title=data['title'])
        obj.save();
        serializer = self.serializer_class(obj)
        return JsonResponse({"audio": serializer.data});

# if the URL is simply visited by a web browser, it returns a list of the non-archived audio files from the database.
    def list(self, request):
        query = self.queryset.filter(archived=False)
        serializer = self.serializer_class(query, many=True)
        return JsonResponse({"audio": serializer.data})

# presumably, if somebody visits /api/audio/*an-integer-value*, then the audio table will be searched for an ID of that value and return the single desired file if it exists and has not been archived.
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
        #print(request.data)
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
        # if self.queryset.filter(audio_id=aid, language_id=lid):
        #     return HttpResponse(status=400)

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
        return JsonResponse({"text": text}, json_dumps_params={'ensure_ascii': False})

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
        print(a)
        print(b)
        if (a == b):
            print(" dsdf")
            self.sameText(a,b,memo)
            print(memo)
        else:
            self.closest_helper(a, b, 0, 0, memo)
        return self.trace(a, b, 0, 0, memo)
    
    def sameText(self,a,b,memo):
        count = len(a)
        for i in range(len(a)): 
            memo[(i,i)] = count
            count -= 1

    def closest_helper(self, a, b, a_index, b_index, memo):
        #print(a_index)
        #print(b_index)
        #print(memo)
        if a_index >= len(a) or b_index >= len(b):
            return 0
        
        if not (a_index, b_index) in memo:
            if a[a_index] == b[b_index]:
                memo[(a_index, b_index)] = 1 + self.closest_helper(a, b, a_index + 1, b_index + 1, memo)
            else:
                memo[(a_index, b_index)] = max(self.closest_helper(a, b, a_index + 1, b_index, memo), self.closest_helper(a, b, a_index, b_index + 1, memo))
        
        print(memo)
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

class AssociationViewSet(viewsets.ModelViewSet):
    """
    Association API
    """
    # permission_classes = [permissions.IsAuthenticated]
    def retrieve(self, request, aid, lid):
        translation = Translation.objects.all().get(audio_id=aid, language_id=lid)
        if not translation:
            return HttpResponse(status=404)
        start = int(request.query_params.get('ts1', 0))
        end = float('inf')
        if 'ts2' in request.query_params:
            end = int(request.query_params['ts2'])
        query = Story.objects.all().filter(translation=translation).order_by('index')
        timestamp_to_word_groups = {}
        word_index = 0
        char_index = 0
        while word_index < len(query):
            obj = query[word_index]
            if obj.timestamp is not None:
                if not obj.timestamp in timestamp_to_word_groups:
                    timestamp_to_word_groups[obj.timestamp] = []
                group = [char_index]
                char_index += len(obj.word)
                if translation.language.spaced:
                    char_index += 1
                word_index += 1

                while word_index < len(query) and (query[word_index].timestamp is None or query[word_index].timestamp == obj.timestamp): # associate timestamps to those without
                    char_index += len(query[word_index].word)
                    if translation.language.spaced:
                        char_index += 1
                    word_index += 1

                group.append(char_index - 1) #inclusive (not exclusive)
                if translation.language.spaced: # remove space at the end
                    group[1] -= 1
                timestamp_to_word_groups[obj.timestamp].append(group)
            else:
                char_index += len(obj.word)
                if translation.language.spaced:
                    char_index += 1
                word_index += 1

        #print(timestamp_to_word_groups)

        next_timestamp = {} # dictionary of timestamp to next timestamp
        ts_query = Story.objects.all().filter(translation=translation).order_by('timestamp').exclude(timestamp__isnull=True)
        for i in range(len(ts_query) - 1):
            next_timestamp[ts_query[i].timestamp] = ts_query[i + 1].timestamp
        next_timestamp[ts_query[len(ts_query) - 1].timestamp] = "end"

        #print("next_ts", next_timestamp)


        start_index = len(query) - 1
        start_offset = 0
        for i in range(len(query)):
            if query[i].timestamp is not None:
                if (next_timestamp[query[i].timestamp] == 'end' or start < next_timestamp[query[i].timestamp]) and end > query[i].timestamp: # interval crossing logic
                    start_index = i
                    break
            start_offset += len(query[i].word)
            if translation.language.spaced:
                start_offset += 1

        end_index = len(query) - 1
        for i in range(len(query) - 1, -1, -1):
            if query[i].timestamp is not None:
                if (next_timestamp[query[i].timestamp] == 'end' or start < next_timestamp[query[i].timestamp]) and end > query[i].timestamp:
                    break
                else:
                    end_index = i - 1

        #print("start_index", start_index, "start_offset", start_offset, "end_index", end_index)


        #Construct output dictionary from information
        output = {}
        associations = {}
        for timestamp_start in timestamp_to_word_groups:
            timestamp_end = next_timestamp[timestamp_start]
            if (timestamp_end == 'end' or timestamp_end > start) and timestamp_start < end:
                entry = []
                for interval in timestamp_to_word_groups[timestamp_start]:
                    # entry.append({'bar':"foo"})
                    # entry.append({'timeStart':str(interval[0] - start_offset),'timeEnd':str(interval[1] - start_offset),'characterStart':str(timestamp_start),'characterEnd':str(timestamp_end)})
                    # timeStart.append(str(interval[0] - start_offset))
                    # timeEnd.append(str(interval[1] - start_offset))
                    # characterStart.append(str(timestamp_start))
                    # characterEnd.append(str(timestamp_end))
                    entry.append(str(interval[0] - start_offset) + "-" + str(interval[1] - start_offset))
                associations[str(timestamp_start) + "-" + str(timestamp_end)] = entry

        text = ""
        words = [query[i].word for i in range(start_index, end_index + 1)]
        if translation.language.spaced:
            text = ' '.join(words)
        else:
            text = "".join(words)

        return JsonResponse({"text": text, "associations": associations}, json_dumps_params={'ensure_ascii': False})



    def update(self, request, aid, lid):
        translation = Translation.objects.all().get(audio_id=aid, language_id=lid)
        if not translation:
            return HttpResponse(status=404)

        query = Story.objects.all().filter(translation=translation).order_by('index')
        serializer = StorySerializer(query, many=True)
        words = [entry['word'] for entry in serializer.data]
        text = ""
        if translation.language.spaced:
            text = ' '.join(words)
        else:
            text = "".join(words)

        start_index = text.find(request.data['text'])
        #print("start_index", start_index)
        if start_index < 0:
            return HttpResponse(status=400)

        # Scan lengths of elements in words
        accumulated_lengths = []
        sum = 0
        for word in words:
            sum += len(word)
            if translation.language.spaced: #account for spaces
                sum += 1
            accumulated_lengths.append(sum - 1) #only want to count until right before start of new word
        if translation.language.spaced: #remove last space at the end
            accumulated_lengths[-1] -= 1
        #print("accumulated lengths", accumulated_lengths)

        changed = []
        #Find corresponding word of index
        association_dict = request.data['associations']
        association_dict = {int(k):v for k,v in association_dict.items()} # make sure the keys in the dict are integers
        for key in association_dict:
            if key >= 0:
                insertion_point = bisect_left(accumulated_lengths, start_index + key)
                # print("insertion point", insertion_point)
                # print(query[insertion_point].timestamp)
                # print(len(words))
                if insertion_point < len(words): #insertion point may exceed words
                    query[insertion_point].timestamp = association_dict[key] #make sure is int
                    changed.append(query[insertion_point])
        
        Story.objects.bulk_update(changed, ['timestamp'])

        query = Story.objects.all().filter(translation=translation).order_by('index')
        serializer = StorySerializer(query, many=True)
        #print(serializer.data)
        return HttpResponse(status=200)
        