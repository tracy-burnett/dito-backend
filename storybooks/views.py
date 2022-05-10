from dataclasses import field
from email.mime import audio
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q
from django.http.response import HttpResponse
from firebase_admin import auth
from storybooks.models import *
from storybooks.s3 import *
from storybooks.serializers import *
from rest_framework import views, viewsets, permissions, generics, filters, status
from rest_framework.response import Response
from bisect import bisect_left
import ast
import secrets
import datetime
import copy


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


class InterpretationViewSet(viewsets.ModelViewSet):
    """
    Interpretation API
    """
    queryset = Interpretation.objects.all()
    serializer_class = InterpretationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, aid):
        data = request.data
        try:
            decoded_token = auth.verify_id_token(request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        if not Audio.objects.filter(Q(id=aid), (Q(public=True) & Q(archived=False))
                    | (Q(shared_with=uid) & Q(archived=False))):
            return HttpResponse(status=404)

        audio = Audio.objects.get(id=aid)
        try:
            obj = Interpretation(public=audio.public, shared_editors=data['shared_editors'],
                    shared_viewers=data['shared_viewers'], audio_id=audio,
                    title=data['title'], latest_text=data['latest_text'],
                    language_name=data['language_name'], spaced_by=data.get('spaced_by', None),
                    created_by=User.get(id=uid), last_edited_by=User.get(id=uid))
        except:
            return JsonResponse({}, status=status.HTTP_404_BAD_REQUEST)
        obj.save()
        return HttpResponse(status=200)

    def retrieve_audios(self, request, aid):
        data = request.data
        try:
            decoded_token = auth.verify_id_token(request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(Q(audio_id__id=aid) | Q(created_by__id=uid) 
                                | (Q(shared_viewers__id=uid) & Q(archived=False))
                                | (Q(shared_editors__id=uid) & Q(archived=False))
                                | (Q(public=True) & Q(archived=False)))
        if not query:
            return HttpResponse(status=404)
        serializer = self.serializer_class(query, many=True)
        return JsonResponse(serializer.data) #TODO

    def retrieve_editors(self, request, iid, aid):
        data = request.data
        try:
             decoded_token = auth.verify_id_token(request.headers['Authorization'])
             uid = decoded_token['uid']
        except:
             return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        
        query = self.queryset.filter(Q(audio_id__id=aid)& Q(created_by__id=uid) 
                                & Q(id=iid) & Q(shared_editors__id=uid) & Q(archived=False))
        if not query:
            return HttpResponse(status=404)
        serializer = self.serializer_class(query, many=True)
        return JsonResponse(serializer.data) #TODO

    def update_editors(self, request, iid, aid):
        data = request.data
        try:
            decoded_token = auth.verify_id_token(request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(Q(audio_id__id=aid) & Q(shared_editors__id=uid) & Q(id=iid) & Q(archived=False))
        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        obj = query.get()

        cpy = Interpretation_History(interpretation_id=obj.id, public=obj.public, shared_editors=obj.shared_editors,
                    shared_viewers=obj.shared_viewers, audio_id=obj.audio_id, title=obj.title, 
                    latest_text=obj.latest_text, archived=obj.archived, language_name=obj.language_name,
                    spaced_by=obj.spaced_by, created_by=obj.created_by, created_at=obj.created_at,
                    last_edited_by=obj.last_edited_by, last_edited_at=obj.last_edited_at, version=obj.version)
        cpy.save()

        modifiable_attr = {'title', 'public', 'language_name', 'latest_text'}
        for key in request.data:
            if hasattr(obj, key) and key in modifiable_attr:
                setattr(obj, key, request.data[key]) #set last updated by/at automatically
            else:
                return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        obj.version += 1
        obj.last_updated_by = User.objects.get(id=uid)
        obj.last_updated_at = datetime.now()
        obj.save()
        return HttpResponse(status=200)

    def retrieve_owners(self, request, iid, aid):
        data = request.data
        try:
            decoded_token = auth.verify_id_token(request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(Q(audio_id__id=aid)& Q(created_by__id=uid) & Q(id=iid))
        if not query:
            return HttpResponse(status=404)
        serializer = self.serializer_class(query, many=True)
        return JsonResponse(serializer.data) #TODO 

    def update_owners(self, request, iid, aid):
        data = request.data
        try:
            decoded_token = auth.verify_id_token(request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(Q(audio_id__id=aid) & Q(created_by__id=uid) & Q(id=iid))
        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        obj = query.get()

        cpy = Interpretation_History(interpretation_id=obj.id, public=obj.public, shared_editors=obj.shared_editors,
                    shared_viewers=obj.shared_viewers, audio_id=obj.audio_id, title=obj.title, 
                    latest_text=obj.latest_text, archived=obj.archived, language_name=obj.language_name,
                    spaced_by=obj.spaced_by, created_by=obj.created_by, created_at=obj.created_at,
                    last_edited_by=obj.last_edited_by, last_edited_at=obj.last_edited_at, version=obj.version)
        cpy.save()

        modifiable_attr = {'public', 'shared_editors', 'shared_viewers', 'audio_id'
                           'title', 'latest_text', 'archived', 'language_name', 'spaced_by'}
        for key in request.data:
            if hasattr(obj, key) and key in modifiable_attr:
                setattr(obj, key, request.data[key]) #set last updated by/at automatically
            else:
                return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        obj.version += 1
        obj.last_updated_by = User.objects.get(id=uid)
        obj.last_updated_at = datetime.now()
        obj.save()
        return HttpResponse(status=200)

    def destroy(self, request, iid, aid):
        data = request.data
        try:
            decoded_token = auth.verify_id_token(request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(Q(audio_id__id=aid) & Q(id=iid) & Q(created_by__id=uid))
        if not query:
            return HttpResponse(status=404)
        obj = query.get()
        cpy = Interpretation_History(interpretation_id=obj.id, public=obj.public, shared_editors=obj.shared_editors,
                    shared_viewers=obj.shared_viewers, audio_id=obj.audio_id, title=obj.title, 
                    latest_text=obj.latest_text, archived=obj.archived, language_name=obj.language_name,
                    spaced_by=obj.spaced_by, created_by=obj.created_by, created_at=obj.created_at,
                    last_edited_by=obj.last_edited_by, last_edited_at=obj.last_edited_at, version=obj.version)
        cpy.save()
        obj.delete()
        return HttpResponse(status=200)

    def retrieve_all(self, request):
        data = request.data
        try:
            decoded_token = auth.verify_id_token(request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(Q(created_by__id=uid) 
                | (Q(shared_viewers__id=uid) & Q(archived=False)) 
                | (Q(shared_editors__id=uid) & Q(archived=False)))
        if not query:
            return HttpResponse(status=404)
        serializer = self.serializer_class(query, many=True)
        return JsonResponse(serializer.data) #TODO

    def retrieve_user(self, request, uid):
        query = self.queryset.filter(Q(archived=False) & Q(public=True) & Q(created_by__id=uid))
        if not query:
            return HttpResponse(status=404)
        serializer = self.serializer_class(query, many=True)
        return JsonResponse(serializer.data) #TODO

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
        # print(request.headers['Authorization'])
        try:
          decoded_token = auth.verify_id_token(request.headers['Authorization'])
          uid = decoded_token['uid']
        except:
          return Response('no valid user logged in')

        # get url from s3 and user from firebase
        obj = Audio(id=data['id'], url=data['url'], title=data['title'], description=data['description'],
                 uploaded_by_id=uid, uploaded_at=datetime.datetime.now(), last_updated_by_id=uid)
        obj.save()
        # serializer = self.serializer_class(obj)
        # return JsonResponse('{"audio": serializer.data}')
        return Response('audio created')

    # Unsafe

    def partial_update_owner(self, request, aid):
        data = request.data

        try:
          decoded_token = auth.verify_id_token(request.headers['Authorization'])
          uid = decoded_token['uid']
        except:
          return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(Q(uploaded_by=uid)& Q(id=aid))
        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        obj = query.get()
        modifiable_attr = {'title', 'public', 'description',
                           'last_updated_by', 'last_updated_at','archived'}
        for key in request.data:
            if hasattr(obj, key) and key in modifiable_attr:
                setattr(obj, key, request.data[key]) #set last updated by/at automatically
            else:
                return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        obj.save()
        serializer = self.serializer_class(obj)
        return JsonResponse(serializer.data)

    def partial_update_editor(self, request,aid):  
        data = request.data

        try:
          decoded_token = auth.verify_id_token(request.headers['Authorization'])
          uid = decoded_token['uid']
        except:
          return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(Q(archived=False) & Q(id=aid) & Q(
            shared_with = uid))
        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        obj = query.get()
        modifiable_attr = {'title', 'public', 'description',
                            'last_updated_by', 'last_updated_at'}
        for key in request.data:
            if hasattr(obj, key) and key in modifiable_attr:
                setattr(obj, key, request.data[key]) #set last updated by/at automatically
            else:
                return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        obj.save()
        serializer = self.serializer_class(obj)
        return JsonResponse(serializer.data)

    def retrieve_public(self, pk):
        query = self.queryset.filter(Q(archived=False) & Q(public=True))
        serializer = self.serializer_class(query, many=True)
        fieldsToKeep = {'title','description','id','url'}
        sanitizedList = []
        for audioModel in serializer.data:
            sanitizedDict = {}
            for key in fieldsToKeep:
                sanitizedDict[key] = audioModel[key]
            sanitizedList.append(sanitizedDict)
        return JsonResponse({"audio":sanitizedList})

    def retrieve_private_user(self, request):
        data = request.headers # FOR DEMONSTRATION
        try:
          decoded_token = auth.verify_id_token(data['Authorization']) # FOR DEMONSTRATION
          uid = decoded_token['uid']
        except:
          return JsonResponse({"login expired; try refreshing the app or loggin in again":status.HTTP_400_BAD_REQUEST})
        # author=Extended_User.objects.get(user_ID=uid) # FOR DEMONSTRATION
        query = self.queryset.filter(Q(uploaded_by_id=uid) | (Q(archived=False) & Q(shared_with=uid))) # FOR DEMONSTRATION

        if not query:
          return JsonResponse({"no storybooks found":status.HTTP_400_BAD_REQUEST})
        serializer = self.serializer_class(query, many=True)
        return JsonResponse({"audio files":serializer.data})
    
    def retrieve_public_user(self, pk,uid):
        query = self.queryset.filter(
            Q(archived=False) & Q(uploaded_by=uid) & Q(public=True))
        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(query, many=True)
        fieldsToKeep = {'title','description','id','url'}
        sanitizedList = []
        for audioModel in serializer.data:
            sanitizedDict = {}
            for key in fieldsToKeep:
                sanitizedDict[key] = audioModel[key]
            sanitizedList.append(sanitizedDict)
        return JsonResponse({"audio":sanitizedList})
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
    # Unsafe (can be overridden)

    def create(self, request, aid, lid):
        try:
          decoded_token = auth.verify_id_token(request.headers['Authorization'])
          uid = decoded_token['uid']
        except:
          return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        print(aid)
        print(lid)
        query = Audio.objects.all().filter(id=aid)
        print(len(query), "hi")
        if not query:
            return HttpResponse(status=404)
        audio = query.get()
        print(lid)
        query = Language.objects.all().filter(id=lid)
        print(query, "2")
        if not query:
            return HttpResponse(status=404)
        language = query.get()

        #Check unique
        # if self.queryset.filter(audio_id=aid, language_id=lid):
        #     return HttpResponse(status=400)

        data = request.data
        print(data, "hidata")
        translation = Translation(
            title=data['title'], text=data['text'], audio_id=aid, language=language, author_id=uid, last_updated_by=uid)
        print(translation)

        text_array = []
        if language.spaced:
            text_array = data['text'].split(" ")
        else:
            text_array = list(data['text'])

        words = []
        for i in range(len(text_array)):
            word = text_array[i]
            words.append(Story(translation=translation, word=word, index=i))
        print(translation, "2")
        translation.save()
        Story.objects.bulk_create(words)
        return Response({'translation created'})

    def retrieve(self, request, aid, lid):
        print(aid)
        print(lid)
        # translation = self.queryset.get(audio_id=aid, language=lid)
        translation = self.queryset.get(audio_id=aid)
        print(translation)
        if not translation:
            return HttpResponse(status=404)
        # if not translation.published:
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

    # Update helper function - finds the closest difference between a and b
    # Returns: a list with integers and tuples
    # If the value is an integer, remove the character with that original index from a
    # If the value is a tuple (i, v), insert v to that original index from a

    def closest(self, a, b):
        memo = {}
        
        if (a == b):
           
            self.sameText(a,b,memo)
       
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
                memo[(a_index, b_index)] = 1 + \
                    self.closest_helper(a, b, a_index + 1, b_index + 1, memo)
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
        translation = self.queryset.get(audio_id=aid)
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
                        add.append(Story(translation=translation,
                                   word=path[path_index][1], index=i + delta))
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
        print("trying to retrieve associations")
        print(aid)
        print(lid)
        translation = Translation.objects.all().get(audio_id=aid)
        print(translation)
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

                # associate timestamps to those without
                while word_index < len(query) and (query[word_index].timestamp is None or query[word_index].timestamp == obj.timestamp):
                    char_index += len(query[word_index].word)
                    if translation.language.spaced:
                        char_index += 1
                    word_index += 1

                group.append(char_index - 1)  # inclusive (not exclusive)
                if translation.language.spaced:  # remove space at the end
                    group[1] -= 1
                timestamp_to_word_groups[obj.timestamp].append(group)
            else:
                char_index += len(obj.word)
                if translation.language.spaced:
                    char_index += 1
                word_index += 1

        # print(timestamp_to_word_groups)

        next_timestamp = {}  # dictionary of timestamp to next timestamp
        ts_query = Story.objects.all().filter(translation=translation).order_by(
            'timestamp').exclude(timestamp__isnull=True)
        for i in range(len(ts_query) - 1):
            next_timestamp[ts_query[i].timestamp] = ts_query[i + 1].timestamp
        if ts_query:
            next_timestamp[ts_query[len(ts_query) - 1].timestamp] = "end"
        else:
            return JsonResponse({"associations": {}}, json_dumps_params={'ensure_ascii': False})


        #print("next_ts", next_timestamp)

        start_index = len(query) - 1
        start_offset = 0
        for i in range(len(query)):
            if query[i].timestamp is not None:
                # interval crossing logic
                if (next_timestamp[query[i].timestamp] == 'end' or start < next_timestamp[query[i].timestamp]) and end > query[i].timestamp:
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

        # Construct output dictionary from information
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
        translation = Translation.objects.all().get(audio_id=aid)
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
            if translation.language.spaced:  # account for spaces
                sum += 1
            # only want to count until right before start of new word
            accumulated_lengths.append(sum - 1)
        if translation.language.spaced:  # remove last space at the end
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
        # print(serializer.data)
        return HttpResponse(status=200)


class ExtendedUserViewSet(viewsets.ModelViewSet):
    
    """
    Extended_User API
    """
    queryset = Extended_User.objects.all()
    serializer_class = ExtendedUserSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        # permission_classes = [permissions.IsAuthenticated]
        data = request.data

        try:
            decoded_token = auth.verify_id_token(request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({'error': 'Firebase authentication failed'}, status=status.HTTP_400_BAD_REQUEST)

        # check if object already exists - create should only work if there isn't already an extended_user for uid
        if Extended_User.objects.filter(user_ID=uid).exists():
            user = Extended_User.objects.get(user_ID=uid)
            if user:
                return JsonResponse({'error': 'user already exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            obj = Extended_User(user_ID=uid,
                            description=data['description'],
                            display_name=data['display_name'],
                            anonymous=data['anonymous'])

            obj.save()
            serializer = self.serializer_class(obj)
            return Response({'user created'})

    def update(self, request):
        data = request.data
        
        try:
            decoded_token = auth.verify_id_token(request.headers['Authorization'])
            uid = decoded_token['uid']
            user = Extended_User.objects.get(user_ID=uid)
            assert(user)
        except:
            print("bad")
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        
        user.description = data['description']
        user.display_name = data['display_name']
        user.anonymous = data['anonymous']
        user.save()
        serializer = self.serializer_class(user)
        return JsonResponse({"user": serializer.data})

    def retrieve(self, request):
        data = request.data
        
        try:
            decoded_token = auth.verify_id_token(request.headers['Authorization'])
            uid = decoded_token['uid']
            user = Extended_User.objects.get(user_ID=uid)
            assert(user)
        except:
            return JsonResponse({'error': 'Firebase authentication failed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # if user.archived:
        #     return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(user)
        return JsonResponse(serializer.data)
