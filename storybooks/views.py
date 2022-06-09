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
        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        ext = request.data['ext']
        audio_ID = secrets.token_urlsafe(8) + ext
        url = S3().get_presigned_url(audio_ID)

        return Response({'url': url, 'audio_ID': audio_ID})


class DownloadFileViewSet(viewsets.ViewSet):
    def presignedgeturl(self, request, pk=None):
        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
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

    def create(self, request, aid):  # updated by skysnolimit 5/9/22
        data = request.data
        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        if not Audio.objects.filter(Q(id=aid)).filter((Q(public=True) & Q(archived=False))
                                                      | (Q(shared_with=uid) & Q(archived=False)) | Q(uploaded_by_id=uid)):
            return HttpResponse(status=404)

        newinterpretationid = secrets.token_urlsafe(8)
        try:
            obj = Interpretation(id=newinterpretationid, public=data['public'],
                                 # shared_editors=data.get('shared_editors', None),
                                 # shared_viewers=data.get('shared_viewers', None),
                                 audio_ID_id=aid,
                                 title=data['title'], latest_text=data['latest_text'],
                                 language_name=data['language_name'],
                                 spaced_by=data.get('spaced_by', None),
                                 created_by_id=uid, last_edited_by_id=uid)
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        text_array = []
        if data['spaced_by']:
            text_array = data['latest_text'].split(data['spaced_by'])
        else:
            text_array = list(data['latest_text'])

        words = []
        for i in range(len(text_array)):
            word = text_array[i]
            words.append(Content(interpretation_id_id=newinterpretationid, audio_id_id=aid,
                         value=word, value_index=i, created_by_id=uid, updated_by_id=uid))
        obj.save()
        Content.objects.bulk_create(words)
        return JsonResponse({"interpretation": {"id": newinterpretationid, "public": data['public'],
                                                "shared_editors": None,
                                                "shared_viewers": None,
                                                "audio_ID": aid,
                                                "title": data['title'], "latest_text": data['latest_text'],
                                                "language_name": data['language_name'],
                                                "spaced_by": None,
                                                "created_by": uid, "last_edited_by": uid}})  # ACTUALLY SHOULD RETURN THE ACTUAL OBJECT, THIS IS KIND OF FAKE

    def retrieve_audios(self, request, aid):
        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(Q(audio_ID_id=aid) & (Q(created_by_id=uid)
                                                           | (Q(shared_viewers__user_ID=uid) & Q(archived=False))
                                                           | (Q(shared_editors__user_ID=uid) & Q(archived=False))
                                                           | (Q(public=True) & Q(archived=False))))
        if not query:
            return HttpResponse(status=404)
        serializer = self.serializer_class(query, many=True)
        # print(serializer.data)
        return JsonResponse({"interpretations": serializer.data})

    def retrieve_editors(self, request, iid, aid):
        data = request.data
        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(Q(audio_id__id=aid) & Q(created_by__id=uid)
                                     & Q(id=iid) & Q(shared_editors__id=uid) & Q(archived=False))
        if not query:
            return HttpResponse(status=404)
        serializer = self.serializer_class(query, many=True)
        return JsonResponse(serializer.data)  # TODO

    def update_editors(self, request, iid, aid):
        data = request.data
        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(Q(audio_id__id=aid) & Q(
            shared_editors__id=uid) & Q(id=iid) & Q(archived=False))
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
                # set last updated by/at automatically
                setattr(obj, key, request.data[key])
            else:
                return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        obj.version += 1
        obj.last_updated_by = User.objects.get(id=uid)
        obj.last_updated_at = datetime.now()
        obj.save()
        return HttpResponse(status=200)

    # UPDATED TO WORK BY SKYSNOLIMIT08 5/11/22
    def retrieve_owners(self, request, iid, aid):
        # print(iid)
        # print(aid)
        # print("hi")
        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.get(
            Q(audio_ID_id=aid) & Q(created_by_id=uid) & Q(id=iid))
        # print(query)
        if not query:
            return HttpResponse(status=404)
        serializer = self.serializer_class(query)
        return JsonResponse({"interpretation": serializer.data}, json_dumps_params={'ensure_ascii': False})

    # UPDATED TO WORK BY SKYSNOLIMIT08 ON 6/9/22
    def update_owners(self, request, iid, aid):
        data = request.data
        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(
            Q(audio_ID_id=aid) & Q(created_by_id=uid) & Q(id=iid))
        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        obj = query.get()

        # make a copy of the former version of the interpretation into the archive

        cpy = Interpretation_History(interpretation_ID=obj.id, public=obj.public, audio_ID=obj.audio_ID, title=obj.title,
                                     latest_text=obj.latest_text, archived=obj.archived, language_name=obj.language_name,
                                     spaced_by=obj.spaced_by, created_by=obj.created_by, created_at=obj.created_at,
                                     last_edited_by=obj.last_edited_by, last_edited_at=obj.last_edited_at, version=obj.version)
        cpy.save()
        Interpretation_History.objects.get(
            interpretation_ID=iid, version=obj.version).shared_editors.set(obj.shared_editors.all())

        # edit the interpretation to reflect the new user entered version

        modifiable_attr = {'public', 'shared_editors', 'shared_viewers', 'audio_id',
                           'title', 'latest_text', 'archived', 'language_name', 'spaced_by'}

        for key in request.data:
            if hasattr(obj, key) and key in modifiable_attr:
                # set last updated by/at automatically
                setattr(obj, key, request.data[key])
            elif key == 'instructions':
                # this is the instructions for updating the content table
                path = request.data[key]
            else:
                return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        # print(obj)
        obj.version += 1
        obj.last_updated_by = uid
        # print(obj)
        obj.save()

        query = Content.objects.all().filter(
            interpretation_id_id=iid).order_by('value_index')
        serializer = ContentSerializer(query, many=True)
        a = [entry['value'] for entry in serializer.data]
        b = []
        if obj.spaced_by:
            b = request.data['latest_text'].split(obj.spaced_by)
        else:
            b = list(request.data['latest_text'])

        # print(path)

        add = []
        subtract = []
        changed = []

        def traverse_path(path):
            i = 0
            while i < len(path):
                if 'moved' in path[i] and path[i]['bIndex'] == -1:
                    useful = [x for x in path if 'moved' in x and not x['bIndex']
                              == -1 and not x['aIndex'] == -1]
                    # print("useful, ", useful)
                    query[path[i]['aIndex']].value_index = useful[0]['bIndex']
                    changed.append(query[path[i]['aIndex']])
                elif path[i]['aIndex'] == -1 and not 'moved' in path[i]:
                    add.append(Content(interpretation_id_id=iid,
                               value=path[i]['line'], value_index=path[i]['bIndex'], audio_id_id=aid, created_by_id=uid, updated_by_id=uid))
                elif path[i]['bIndex'] == -1 and not 'moved' in path[i]:
                    subtract.append(query[path[i]['aIndex']])
                elif not 'moved' in path[i]:
                    query[path[i]['aIndex']].value_index = path[i]['bIndex']
                    changed.append(query[path[i]['aIndex']])

                i += 1
        traverse_path(path['lines'])

        # print("changed, ", changed[0].__dict__)
        # print("add, ", add[0].__dict__)
        # print("subtract, ", subtract[0].__dict__)

        Content.objects.bulk_update(changed, ['value_index'])
        for obj in subtract:
            obj.delete()
        Content.objects.bulk_create(add)

        # query = Content.objects.all().filter(interpretation_id_id=iid).order_by('value_index') # just for debugging; can safely comment this out
        # serializer = ContentSerializer(query, many=True) # just for debugging;  can safely comment this out
        # a = [entry['value'] for entry in serializer.data] # just for debugging;  can safely comment this out
        # print("".join(a))
        # print(" ")
        # print("".join(b))
        # print("DID IT WORK?", a==b) # just for debugging;  can safely comment this out

        return HttpResponse(status=200)

    def destroy(self, request, iid, aid):
        data = request.data
        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(
            Q(audio_id__id=aid) & Q(id=iid) & Q(created_by__id=uid))
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
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(Q(created_by__id=uid)
                                     | (Q(shared_viewers__id=uid) & Q(archived=False))
                                     | (Q(shared_editors__id=uid) & Q(archived=False)))
        if not query:
            return HttpResponse(status=404)
        serializer = self.serializer_class(query, many=True)
        return JsonResponse(serializer.data)  # TODO

    def retrieve_user(self, request, uid):
        query = self.queryset.filter(Q(archived=False) & Q(
            public=True) & Q(created_by__id=uid))
        if not query:
            return HttpResponse(status=404)
        serializer = self.serializer_class(query, many=True)
        return JsonResponse(serializer.data)  # TODO


class AudioViewSet(viewsets.ModelViewSet):
    """
    Audio API
    """
    queryset = Audio.objects.all()
    serializer_class = AudioSerializer
    # this overrides project-level permission in settings.py
    permission_classes = [permissions.AllowAny]

# presumably, somebody posts two fields, url and title, to the URL, then it creates a new audio object in the database.
    def create(self, request):
        data = request.data
        # print(request.headers['Authorization'])
        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
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
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(Q(uploaded_by=uid) & Q(id=aid))
        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        obj = query.get()
        modifiable_attr = {'title', 'public', 'description',
                           'last_updated_by', 'last_updated_at', 'archived'}
        for key in request.data:
            if hasattr(obj, key) and key in modifiable_attr:
                # set last updated by/at automatically
                setattr(obj, key, request.data[key])
            else:
                return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        obj.save()
        serializer = self.serializer_class(obj)
        return JsonResponse(serializer.data)

    def partial_update_editor(self, request, aid):
        data = request.data

        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.filter(Q(archived=False) & Q(id=aid) & Q(
            shared_with=uid))
        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        obj = query.get()
        modifiable_attr = {'title', 'public', 'description',
                           'last_updated_by', 'last_updated_at'}
        for key in request.data:
            if hasattr(obj, key) and key in modifiable_attr:
                # set last updated by/at automatically
                setattr(obj, key, request.data[key])
            else:
                return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        obj.save()
        serializer = self.serializer_class(obj)
        return JsonResponse(serializer.data)

    def retrieve_public(self, pk):
        query = self.queryset.filter(Q(archived=False) & Q(public=True))
        serializer = self.serializer_class(query, many=True)
        fieldsToKeep = {'title', 'description', 'id', 'url'}
        sanitizedList = []
        for audioModel in serializer.data:
            sanitizedDict = {}
            for key in fieldsToKeep:
                sanitizedDict[key] = audioModel[key]
            sanitizedList.append(sanitizedDict)
        return JsonResponse({"audio": sanitizedList})

    def retrieve_private_user(self, request):
        data = request.headers  # FOR DEMONSTRATION
        try:
            decoded_token = auth.verify_id_token(
                data['Authorization'])  # FOR DEMONSTRATION
            uid = decoded_token['uid']
        except:
            return JsonResponse({"login expired; try refreshing the app or loggin in again": status.HTTP_400_BAD_REQUEST})
        # author=Extended_User.objects.get(user_ID=uid) # FOR DEMONSTRATION
        query = self.queryset.filter(Q(uploaded_by_id=uid) | (
            Q(archived=False) & Q(shared_with=uid)))  # FOR DEMONSTRATION

        if not query:
            return JsonResponse({"no storybooks found": status.HTTP_400_BAD_REQUEST})
        serializer = self.serializer_class(query, many=True)
        return JsonResponse({"audio files": serializer.data})

    def retrieve_public_user(self, pk, uid):
        query = self.queryset.filter(
            Q(archived=False) & Q(uploaded_by=uid) & Q(public=True))
        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(query, many=True)
        fieldsToKeep = {'title', 'description', 'id', 'url'}
        sanitizedList = []
        for audioModel in serializer.data:
            sanitizedDict = {}
            for key in fieldsToKeep:
                sanitizedDict[key] = audioModel[key]
            sanitizedList.append(sanitizedDict)
        return JsonResponse({"audio": sanitizedList})

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
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        # print(aid)
        # print(lid)
        query = Audio.objects.all().filter(id=aid)
        # print(len(query), "hi")
        if not query:
            return HttpResponse(status=404)
        audio = query.get()
        # print(lid)
        query = Language.objects.all().filter(id=lid)
        # print(query, "2")
        if not query:
            return HttpResponse(status=404)
        language = query.get()

        # Check unique
        # if self.queryset.filter(audio_id=aid, language_id=lid):
        #     return HttpResponse(status=400)

        data = request.data
        # print(data, "hidata")
        translation = Translation(
            title=data['title'], text=data['text'], audio_id=aid, language=language, author_id=uid, last_updated_by=uid)
        # print(translation)

        text_array = []
        if language.spaced:
            text_array = data['text'].split(" ")
        else:
            text_array = list(data['text'])

        words = []
        for i in range(len(text_array)):
            word = text_array[i]
            words.append(Story(translation=translation, word=word, index=i))
        # print(translation, "2")
        translation.save()
        Story.objects.bulk_create(words)
        return Response({'translation created'})

    def retrieve(self, request, aid, lid):
        # print(aid)
        # print(lid)
        # translation = self.queryset.get(audio_id=aid, language=lid)
        translation = self.queryset.get(audio_id=aid)
        # print(translation)
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

        # if (a == b):

        # self.sameText(a,b,memo)

        # else:
        self.closest_helper(a, b, 0, 0, memo)
        return self.trace(a, b, 0, 0, memo)

    # def sameText(self,a,b,memo):
    #     count = len(a)
    #     for i in range(len(a)):
    #         memo[(i,i)] = count
    #         count -= 1

    def closest_helper(self, a, b, a_index, b_index, memo):
        # print(a_index)
        # print(b_index)
        # print(memo)
        if a_index >= len(a) or b_index >= len(b):
            return 0

        if not (a_index, b_index) in memo:
            if a[a_index] == b[b_index]:
                memo[(a_index, b_index)] = 1 + \
                    self.closest_helper(a, b, a_index + 1, b_index + 1, memo)
            else:

                memo[(a_index, b_index)] = max(self.closest_helper(a, b, a_index + 1,
                                                                   b_index, memo), self.closest_helper(a, b, a_index, b_index + 1, memo))

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
        # print("path:", path)
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

    def retrieve(self, request, aid, iid):     # UPDATED BY SKYSNOLIMIT08 TO WORK
        # print("trying to retrieve associations")
        # print(aid)
        # print(iid)
        interpretation = Interpretation.objects.all().get(audio_ID_id=aid, id=iid)
        # print(interpretation)
        if not interpretation:
            return HttpResponse(status=404)
        start = int(request.query_params.get('ts1', 0))
        end = float('inf')
        if 'ts2' in request.query_params:
            end = int(request.query_params['ts2'])
        query = Content.objects.all().filter(
            interpretation_id_id=iid).order_by('value_index')
        timestamp_to_word_groups = {}
        word_index = 0
        char_index = 0
        while word_index < len(query):
            obj = query[word_index]
            if obj.audio_time is not None:
                if not obj.audio_time in timestamp_to_word_groups:
                    timestamp_to_word_groups[obj.audio_time] = []
                group = [char_index]
                char_index += len(obj.value)
                if interpretation.spaced_by:
                    char_index += 1
                word_index += 1

                # associate timestamps to those without
                while word_index < len(query) and (query[word_index].audio_time is None or query[word_index].audio_time == obj.audio_time):
                    char_index += len(query[word_index].value)
                    if interpretation.spaced_by:
                        char_index += 1
                    word_index += 1

                group.append(char_index - 1)  # inclusive (not exclusive)
                if interpretation.spaced_by:  # remove space at the end
                    group[1] -= 1
                timestamp_to_word_groups[obj.audio_time].append(group)
            else:
                char_index += len(obj.value)
                if interpretation.spaced_by:
                    char_index += 1
                word_index += 1

        # print(timestamp_to_word_groups)

        next_timestamp = {}  # dictionary of timestamp to next timestamp
        ts_query = Content.objects.all().filter(interpretation_id_id=iid).order_by(
            'audio_time').exclude(audio_time__isnull=True)
        for i in range(len(ts_query) - 1):
            next_timestamp[ts_query[i].audio_time] = ts_query[i + 1].audio_time
        if ts_query:
            next_timestamp[ts_query[len(ts_query) - 1].audio_time] = "end"
        else:
            return JsonResponse({"associations": {}}, json_dumps_params={'ensure_ascii': False})

        #print("next_ts", next_timestamp)

        start_index = len(query) - 1
        start_offset = 0
        for i in range(len(query)):
            if query[i].audio_time is not None:
                # interval crossing logic
                if (next_timestamp[query[i].audio_time] == 'end' or start < next_timestamp[query[i].audio_time]) and end > query[i].audio_time:
                    start_index = i
                    break
            start_offset += len(query[i].value)
            if interpretation.spaced_by:
                start_offset += 1

        end_index = len(query) - 1
        for i in range(len(query) - 1, -1, -1):
            if query[i].audio_time is not None:
                if (next_timestamp[query[i].audio_time] == 'end' or start < next_timestamp[query[i].audio_time]) and end > query[i].audio_time:
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
                    entry.append(
                        str(interval[0] - start_offset) + "-" + str(interval[1] - start_offset))
                associations[str(timestamp_start) + "-" +
                             str(timestamp_end)] = entry

        # text = ""
        # words = [query[i].word for i in range(start_index, end_index + 1)]
        # if translation.language.spaced:
        #     text = ' '.join(words)
        # else:
        #     text = "".join(words)

        return JsonResponse({"associations": associations}, json_dumps_params={'ensure_ascii': False})

    def update(self, request, aid, iid):  # UPDATED 6/9/22 BY SKYSNOLIMIT08 TO WORK
        
        try:
            decoded_token = auth.verify_id_token(request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        if not Interpretation.objects.filter(Q(audio_ID_id=aid, id=iid)).filter((Q(public=True) & Q(archived=False))
                                                      | (Q(shared_editors=uid) & Q(archived=False)) | Q(created_by_id=uid)):
            return HttpResponse(status=404)

        query = Content.objects.all().filter(
            interpretation_id_id=iid).order_by('value_index')

        changed = []
        association_dict = request.data['associations']
        # make sure the keys in the dict are integers
        association_dict = {int(k): v for k, v in association_dict.items()}
        for key in association_dict:
            if key >= 0:
                    query[key].audio_time = association_dict[key]
                    changed.append(query[key])

        Content.objects.bulk_update(changed, ['audio_time'])

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
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
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
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
            user = Extended_User.objects.get(user_ID=uid)
            assert(user)
        except:
            # print("bad")
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
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
            user = Extended_User.objects.get(user_ID=uid)
            assert(user)
        except:
            return JsonResponse({'error': 'Firebase authentication failed'}, status=status.HTTP_400_BAD_REQUEST)

        # if user.archived:
        #     return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(user)
        return JsonResponse(serializer.data)
