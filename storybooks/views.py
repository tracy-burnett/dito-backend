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
import re
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
    queryset = Audio.objects.all()
    serializer_class = AudioSerializer

    def presignedgeturl(self, request, pk=None):
        audio_ID = request.data['audio_ID']

        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            query = self.queryset.prefetch_related('shared_editors', 'shared_viewers', 'uploaded_by').filter((Q(uploaded_by=decoded_token['uid']) | (Q(archived=False) & Q(shared_editors=decoded_token['uid'])) | (
                Q(archived=False) & Q(shared_viewers=decoded_token['uid'])) | Q(public=True) & Q(archived=False)) & Q(id=audio_ID)).distinct()
        except:
            query = self.queryset.filter(
                Q(public=True) & Q(archived=False) & Q(id=audio_ID))

        if not query:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        elif query:
            url = S3().get_file(audio_ID)
            serializer = self.serializer_class(query[0])
            peaks = serializer.data['peaks']

            return Response({'url': url, 'peaks': peaks})


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
        obj = Audio(id=data['id'], url=request.headers['Origin'], title=data['title'], description=data['description'],
                    uploaded_by_id=uid, uploaded_at=datetime.datetime.now(), last_updated_by_id=uid)
        obj.save()
        serializer = self.serializer_class(obj)
        # return JsonResponse('{"audio": serializer.data}')
        return JsonResponse(serializer.data)

    def retrieve_public(self, request):
        data = request.headers
        # print(data)
        query = self.queryset.filter(Q(archived=False) & Q(
            public=True) & Q(url=data['Origin']))
        serializer = AudioSerializerPublic(query, many=True)
        return JsonResponse({"audio": serializer.data})

    def partial_update_owner(self, request, aid):
        data = request.data

        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.prefetch_related(
            'uploaded_by').filter(Q(uploaded_by=uid) & Q(id=aid))
        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        obj = query.get()
        modifiable_attr = {'title', 'public', 'description',
                           'last_updated_by', 'last_updated_at', 'archived'}
        k = 0
        for key in request.data:
            if hasattr(obj, key) and key in modifiable_attr:
                # set last updated by/at automatically
                setattr(obj, key, request.data[key])
                k = 1
        if 'shared_editor' in request.data and request.data['shared_editor'] != None:
            # print("editor", request.data['shared_editor'])
            neweditor = Extended_User.objects.get(
                email=request.data['shared_editor'])
            obj.shared_editors.add(neweditor)
            k = 1
        if 'shared_viewer' in request.data and request.data['shared_viewer'] != None:
            # print("viewer", request.data['shared_viewer'])
            newviewer = Extended_User.objects.get(
                email=request.data['shared_viewer'])
            obj.shared_viewers.add(newviewer)
            k = 1
        if 'remove_editor' in request.data:
            # print("editor", request.data['remove_editor'])
            oldeditor = Extended_User.objects.get(
                user_ID=request.data['remove_editor'])
            obj.shared_editors.remove(oldeditor)
            k = 1
        if 'remove_viewer' in request.data:
            # print("viewer", request.data['remove_viewer'])
            oldviewer = Extended_User.objects.get(
                user_ID=request.data['remove_viewer'])
            obj.shared_viewers.remove(oldviewer)
            k = 1
        if k == 0:
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

        query = self.queryset.prefetch_related('shared_editors').filter(Q(archived=False) & Q(id=aid) & Q(
            shared_editors=uid))
        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        obj = query.get()
        modifiable_attr = {'title', 'public', 'description',
                           'last_updated_by', 'last_updated_at'}
        k = 0
        for key in request.data:
            if hasattr(obj, key) and key in modifiable_attr:
                # set last updated by/at automatically
                setattr(obj, key, request.data[key])
                k = 1
        if 'shared_viewer' in request.data and request.data['shared_viewer'] != None:
            # print("viewer", request.data['shared_viewer'])
            newviewer = Extended_User.objects.get(
                email=request.data['shared_viewer'])
            obj.shared_viewers.add(newviewer)
            k = 1
        if 'remove_viewer' in request.data:
            # print("viewer", request.data['remove_viewer'])
            oldviewer = Extended_User.objects.get(
                user_ID=request.data['remove_viewer'])
            obj.shared_viewers.remove(oldviewer)
            k = 1
        if k == 0:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        obj.save()
        serializer = self.serializer_class(obj)
        return JsonResponse(serializer.data)

    def partial_update_public(self, request, aid):
        data = request.data

        query = self.queryset.filter(id=aid)
        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        obj = query.get()
        modifiable_attr = {'peaks'}
        k = 0
        for key in request.data:
            if hasattr(obj, key) and key in modifiable_attr:
                setattr(obj, key, request.data[key])
                k = 1

        if k == 0:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        obj.save()
        return Response({'peaks created'})

    def retrieve_private_user(self, request):
        data = request.headers  # FOR DEMONSTRATION
        try:
            decoded_token = auth.verify_id_token(
                data['Authorization'])  # FOR DEMONSTRATION
            uid = decoded_token['uid']
        except:
            return JsonResponse({"login expired; try refreshing the app or logging in again": status.HTTP_400_BAD_REQUEST})
        # author=Extended_User.objects.get(user_ID=uid) # FOR DEMONSTRATION
        query = self.queryset.prefetch_related('uploaded_by', 'shared_editors', 'shared_viewers').filter((Q(uploaded_by_id=uid) | (
            Q(archived=False) & Q(shared_editors=uid)) | (
            Q(archived=False) & Q(shared_viewers=uid)) | (
            Q(archived=False) & Q(public=True))) & Q(url=data['Origin'])).distinct()  # FOR DEMONSTRATION

        if not query:
            return JsonResponse({"no storybooks found": status.HTTP_400_BAD_REQUEST})

        # serializer = AudioSerializer2(query, many=True)

        query1 = []
        query2 = []

        query1 = query.filter(Q(uploaded_by_id=uid) |
                              Q(shared_editors=uid)).distinct()
        query2 = query.filter(
            (~Q(uploaded_by_id=uid) & ~Q(shared_editors=uid))).distinct()

        # does show display names of editors
        serializer1 = AudioSerializer2(query1, many=True)
        # doesn't show display names of editors
        serializer2 = AudioSerializer3(query2, many=True)

        serializeddata = serializer1.data + serializer2.data

        return JsonResponse({"audio files": serializeddata})


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

        if not Audio.objects.prefetch_related('shared_editors', 'shared_viewers', 'uploaded_by').filter(Q(id=aid)).filter((Q(public=True) & Q(archived=False))
                                                                                                                          | (Q(shared_editors=uid) & Q(archived=False)) | (
                Q(archived=False) & Q(shared_viewers=uid)) | Q(uploaded_by_id=uid)).distinct():
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

        regexwithspacedby = re.escape(data['spaced_by']) + r"|(\n)"

        if data['spaced_by']:
            text_array = re.split(regexwithspacedby, data['latest_text'])
            # print(text_array)
            # print(len(text_array)-1)
            startinglength = len(text_array)
            for p in range(startinglength):
                if text_array[startinglength-1-p] == "" or text_array[startinglength-1-p] == None:
                    # print(len(text_array)-1-p)
                    # print(text_array[len(text_array)-1-p])
                    del text_array[startinglength-1-p]
            # print(text_array)

        else:
            text_array = list(data['latest_text'])

        # print(text_array)
        words = []
        for i in range(len(text_array)):
            word = text_array[i]
            words.append(Content(interpretation_id_id=newinterpretationid, audio_id_id=aid,
                         value=word, value_index=i, created_by_id=uid, updated_by_id=uid))
            # if i < 21:
            #     print(i)
            #     print(word)
            # if word == None:
            #     print(i)
        obj.save()
        Content.objects.bulk_create(words)

        serializer = self.serializer_class(obj)
        return JsonResponse({"interpretation": serializer.data})

    def retrieve_audios(self, request, aid):
        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']

            query = self.queryset.prefetch_related('shared_editors', 'shared_viewers', 'created_by', 'audio_ID').filter(Q(audio_ID_id=aid) & (Q(created_by_id=uid)
                                                                                                                                              | (Q(shared_viewers__user_ID=uid) & Q(archived=False))
                                                                                                                                              | (Q(shared_editors__user_ID=uid) & Q(archived=False))
                                                                                                                                              | (Q(public=True) & Q(archived=False)))).distinct()
        except:
            uid = ""
            query = self.queryset.prefetch_related('audio_ID').filter(Q(audio_ID_id=aid) & (
                Q(public=True) & Q(archived=False)))

        if not query:
            return HttpResponse(status=404)
        # serializer = self.serializer_class(query, many=True)

        query1 = []
        query2 = []

        query1 = query.filter(Q(created_by_id=uid) | Q(
            shared_editors__user_ID=uid)).distinct()
        query2 = query.filter((~Q(created_by_id=uid) & ~Q(
            shared_editors__user_ID=uid))).distinct()

        # does show display names of editors
        serializer1 = InterpretationSerializer(query1, many=True)
        # doesn't show display names of editors
        serializer2 = InterpretationSerializer2(query2, many=True)

        serializeddata = serializer1.data + serializer2.data

        # print(serializer.data)
        return JsonResponse({"interpretations": serializeddata})

    def retrieve_editors(self, request, iid, aid):
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
            Q(audio_ID_id=aid) & Q(shared_editors=uid) & Q(archived=False) & Q(id=iid))
        # print(query)
        if not query:
            return HttpResponse(status=404)

        serializer = InterpretationSerializerBrief(query)
        return JsonResponse({"interpretation": serializer.data}, json_dumps_params={'ensure_ascii': False})

    def retrieve_viewers(self, request, iid, aid):
        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']

            query = self.queryset.get(
                Q(audio_ID_id=aid) & Q(shared_viewers=uid) & Q(archived=False) & Q(id=iid))
        except:
            query = self.queryset.get(
                Q(audio_ID_id=aid) & Q(public=True) & Q(archived=False) & Q(id=iid))

        # print(query)
        if not query:
            return HttpResponse(status=404)
        serializer = InterpretationSerializerBrief(query)
        return JsonResponse({"interpretation": serializer.data}, json_dumps_params={'ensure_ascii': False})

    # UPDATED TO WORK BY SKYSNOLIMIT08 ON 6/9/22

    def update_editors(self, request, iid, aid):
        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        query = self.queryset.prefetch_related('audio_ID', 'shared_editors').filter(
            Q(audio_ID_id=aid) & Q(shared_editors__user_ID=uid) & Q(id=iid) & Q(archived=False))

        if not query:
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        obj = query.get()

        # make a copy of the former version of the interpretation into the archive

        cpy = Interpretation_History(interpretation_ID=obj.id, public=obj.public, audio_ID=obj.audio_ID, title=obj.title,
                                     latest_text=obj.latest_text, archived=obj.archived, language_name=obj.language_name,
                                     spaced_by=obj.spaced_by, created_by=obj.created_by, created_at=obj.created_at,
                                     last_edited_by=obj.last_edited_by, last_edited_at=obj.last_edited_at, version=obj.version)
        cpy.save()
        try:
            Interpretation_History.objects.get(
                interpretation_ID=iid, version=obj.version).shared_editors.set(obj.shared_editors.all())
            print('specified which users were allowed to edit the OLD version of the interpretation')
            Interpretation_History.objects.get(
                interpretation_ID=iid, version=obj.version).shared_viewers.set(obj.shared_viewers.all())
            print('specified which users were allowed to see the OLD version of the interpretation')
        except:
            print('failed to specify which users were allowed to see or which were allowed to edit the old interpretation')


        # edit the interpretation to reflect the new user entered version

        modifiable_attr = {'public', 'shared_viewers',
                           'title', 'latest_text', 'language_name'}

        k = 0
        for key in request.data:
            if hasattr(obj, key) and key in modifiable_attr:
                # set last updated by/at automatically
                setattr(obj, key, request.data[key])
                k = 1
        if 'shared_viewer' in request.data and request.data['shared_viewer'] != None:
            # print("viewer", request.data['shared_viewer'])
            newviewer = Extended_User.objects.get(
                email=request.data['shared_viewer'])
            obj.shared_viewers.add(newviewer)
            k = 1
        if 'remove_viewer' in request.data:
            # print("viewer", request.data['remove_viewer'])
            oldviewer = Extended_User.objects.get(
                user_ID=request.data['remove_viewer'])
            obj.shared_viewers.remove(oldviewer)
            k = 1
        if key == 'instructions':
            # this is the instructions for updating the content table
            path = request.data[key]
            k = 1
        if k == 0:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        # print(obj)
        obj.version += 1
        obj.last_updated_by = uid
        # print(obj)
        if obj.title == "" and obj.latest_text == "" and obj.language_name == "":
            obj.delete()
            return Response('interpretation deleted')
        else:
            obj.save()

            if 'path' in locals():
                query = Content.objects.all().prefetch_related('interpretation_id').filter(
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

                    useful = [x for x in path if 'moved' in x and not x['bIndex']
                              == -1 and not x['aIndex'] == -1]
                    while i < len(path):
                        if 'moved' in path[i] and path[i]['bIndex'] == -1:
                            # print(path[i]) # print instructions
                            for use in useful:
                                if use['line'] == path[i]['line']:
                                    usefulnow = use
                                    useful.remove(use)
                                    break
                            # print(usefulnow)
                            query[path[i]['aIndex']
                                  ].value_index = usefulnow['bIndex']
                            changed.append(query[path[i]['aIndex']])

                        elif path[i]['aIndex'] == -1 and not 'moved' in path[i]:
                            # print("in added")
                            add.append(Content(interpretation_id_id=iid,
                                               value=path[i]['line'], value_index=path[i]['bIndex'], audio_id_id=aid, created_by_id=uid, updated_by_id=uid))
                        elif path[i]['bIndex'] == -1 and not 'moved' in path[i]:
                            # print("in subtracted")
                            subtract.append(query[path[i]['aIndex']])
                        elif not 'moved' in path[i]:
                            # print("in changed")
                            query[path[i]['aIndex']
                                  ].value_index = path[i]['bIndex']
                            changed.append(query[path[i]['aIndex']])

                        # print("finished path")
                        i += 1
                traverse_path(path['lines'])

                # print("changed, ", changed[0].__dict__)
                # print("add, ", add[0].__dict__)
                # print("subtract, ", subtract[0].__dict__)

                Content.objects.bulk_update(changed, ['value_index'])
                for obj in subtract:
                    obj.delete()
                Content.objects.bulk_create(add)
            return Response('interpretation updated')

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
        serializer = InterpretationSerializerBrief(query)
        return JsonResponse({"interpretation": serializer.data}, json_dumps_params={'ensure_ascii': False})

    # UPDATED TO WORK BY SKYSNOLIMIT08 ON 6/9/22
    def update_owners(self, request, iid, aid):
        print('debugging endpoint')

        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            print('user authentication failed')
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        print('user authentication succeeded')
        query = self.queryset.prefetch_related('audio_ID', 'created_by').filter(
            Q(audio_ID_id=aid) & Q(created_by_id=uid) & Q(id=iid))
        if not query:
            print('interpretation with the specified parameters not found')
            return JsonResponse({}, status=status.HTTP_404_NOT_FOUND)
        obj = query.get()
        print('interpretation located in database')

        # make a copy of the former version of the interpretation into the archive

        cpy = Interpretation_History(interpretation_ID=obj.id, public=obj.public, audio_ID=obj.audio_ID, title=obj.title,
                                     latest_text=obj.latest_text, archived=obj.archived, language_name=obj.language_name,
                                     spaced_by=obj.spaced_by, created_by=obj.created_by, created_at=obj.created_at,
                                     last_edited_by=obj.last_edited_by, last_edited_at=obj.last_edited_at, version=obj.version)
        print('backup of old interpretation created')
        cpy.save()
        print('backup of old interpretation saved')
        try:
            Interpretation_History.objects.get(
                interpretation_ID=iid, version=obj.version).shared_editors.set(obj.shared_editors.all())
            print('specified which users were allowed to edit the OLD version of the interpretation')
            Interpretation_History.objects.get(
                interpretation_ID=iid, version=obj.version).shared_viewers.set(obj.shared_viewers.all())
            print('specified which users were allowed to see the OLD version of the interpretation')
        except:
            print('failed to specify which users were allowed to see or which were allowed to edit the old interpretation')

        # edit the interpretation to reflect the new user entered version

        modifiable_attr = {'public', 'shared_editors', 'shared_viewers', 'audio_id',
                           'title', 'latest_text', 'archived', 'language_name', }

        print('specified which attributes of the old interpretation we are allowed to change in the new interpretation')


        k = 0
        for key in request.data:
            if hasattr(obj, key) and key in modifiable_attr:
                # set last updated by/at automatically
                setattr(obj, key, request.data[key])
                k = 1
        if 'shared_editor' in request.data and request.data['shared_editor'] != None:
            # print("editor", request.data['shared_editor'])
            neweditor = Extended_User.objects.get(
                email=request.data['shared_editor'])
            obj.shared_editors.add(neweditor)
            k = 1
        if 'shared_viewer' in request.data and request.data['shared_viewer'] != None:
            # print("viewer", request.data['shared_viewer'])
            newviewer = Extended_User.objects.get(
                email=request.data['shared_viewer'])
            obj.shared_viewers.add(newviewer)
            k = 1
        if 'remove_editor' in request.data:
            # print("editor", request.data['remove_editor'])
            oldeditor = Extended_User.objects.get(
                user_ID=request.data['remove_editor'])
            obj.shared_editors.remove(oldeditor)
            k = 1
        if 'remove_viewer' in request.data:
            # print("viewer", request.data['remove_viewer'])
            oldviewer = Extended_User.objects.get(
                user_ID=request.data['remove_viewer'])
            obj.shared_viewers.remove(oldviewer)
            k = 1
        if key == 'instructions':
            # this is the instructions for updating the content table
            path = request.data[key]
            k = 1
        if k == 0:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        print('updated the relevant attributes to create the new interpretation version')

        # print(obj)
        obj.version += 1
        print('gave object a new version number')

        obj.last_updated_by = uid
        print('specified which user created this new version')

        # print(obj)
        if obj.title == "" and obj.latest_text == "" and obj.language_name == "":
            obj.delete()
            print('deleted the interpretation because new version is empty')
            return Response('interpretation deleted')
        else:
            print('saved the new version')
            obj.save()

            if 'path' in locals():
                print('beginning to update timestamps')
                query = Content.objects.all().prefetch_related('interpretation_id').filter(
                    interpretation_id_id=iid).order_by('value_index')
                
                print('collected the old timestamps')
                serializer = ContentSerializer(query, many=True)

                print('set the timestamp serializer')
                a = [entry['value'] for entry in serializer.data]
                b = []
                if obj.spaced_by:
                    print('text has a tokenizer')
                    b = request.data['latest_text'].split(obj.spaced_by)
                    print('text now split by tokenizer')
                else:
                    print('text has not tokenizer')
                    b = list(request.data['latest_text'])
                    print('text now split by character')

                # print(path)

                add = []
                subtract = []
                changed = []

                def traverse_path(path):
                    print('starting to review what changes to timestamps should be made')
                    i = 0

                    useful = [x for x in path if 'moved' in x and not x['bIndex']
                              == -1 and not x['aIndex'] == -1]
                    print('refined the instructions')

                    while i < len(path):
                        if 'moved' in path[i] and path[i]['bIndex'] == -1:
                            # print(path[i]) # print instructions
                            for use in useful:
                                if use['line'] == path[i]['line']:
                                    usefulnow = use
                                    useful.remove(use)
                                    break
                            # print(usefulnow)
                            query[path[i]['aIndex']
                                  ].value_index = usefulnow['bIndex']
                            changed.append(query[path[i]['aIndex']])

                        elif path[i]['aIndex'] == -1 and not 'moved' in path[i]:
                            # print("in added")
                            add.append(Content(interpretation_id_id=iid,
                                               value=path[i]['line'], value_index=path[i]['bIndex'], audio_id_id=aid, created_by_id=uid, updated_by_id=uid))
                        elif path[i]['bIndex'] == -1 and not 'moved' in path[i]:
                            # print("in subtracted")
                            subtract.append(query[path[i]['aIndex']])
                        elif not 'moved' in path[i]:
                            # print("in changed")
                            query[path[i]['aIndex']
                                  ].value_index = path[i]['bIndex']
                            changed.append(query[path[i]['aIndex']])

                        # print("finished path")
                        i += 1
                    print('finished traversing the path')
                traverse_path(path['lines'])

                # print("changed, ", changed[0].__dict__)
                # print("add, ", add[0].__dict__)
                # print("subtract, ", subtract[0].__dict__)

                Content.objects.bulk_update(changed, ['value_index'])
                for obj in subtract:
                    obj.delete()
                Content.objects.bulk_create(add)
                print('all changes made')

            print('success')
            return Response('interpretation updated')

    # def retrieve_all(self, request):
    #     data = request.data
    #     try:
    #         decoded_token = auth.verify_id_token(
    #             request.headers['Authorization'])
    #         uid = decoded_token['uid']
    #     except:
    #         return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

    #     query = self.queryset.prefetch_related('shared_editors', 'shared_viewers','created_by').filter(Q(created_by__id=uid)
    #                                  | (Q(shared_viewers__id=uid) & Q(archived=False))
    #                                  | (Q(shared_editors__id=uid) & Q(archived=False))).distinct()
    #     if not query:
    #         return HttpResponse(status=404)
    #     serializer = self.serializer_class(query, many=True)
    #     return JsonResponse(serializer.data)  # TODO


class AssociationViewSet(viewsets.ModelViewSet):
    """
    Association API
    """
    # permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, aid, iid, timestep):

        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            uid = ""

        interpretation = Interpretation.objects.all().prefetch_related('shared_editors', 'shared_viewers', 'created_by', 'audio_ID').get(Q(audio_ID_id=aid) & Q(id=iid) & ((Q(created_by_id=uid)
                                                                                                                                                                            | (Q(shared_viewers__user_ID=uid) & Q(archived=False))
                                                                                                                                                                           | (Q(shared_editors__user_ID=uid) & Q(archived=False))
                                                                                                                                                                            | (Q(public=True) & Q(archived=False)))))

        if not interpretation:
            return HttpResponse(status=404)

        query = Content.objects.all().prefetch_related('audio_id', 'interpretation_id').filter(audio_id_id=aid,
                                                                                               interpretation_id_id=iid).exclude(audio_time=None).order_by('audio_time')
        if not query:
            return JsonResponse({"associations": {}}, json_dumps_params={'ensure_ascii': False})

        a = timestep  # maximum number of time to group timestamps together for
        associations_times = []
        associations_chars = []
        associations_offsets = []
        # print("test")
        # print(len(interpretation.spaced_by))
        # if the interpretation is spaced, I need to duplicate each word and create a "value_index" representing the first character of the word and a "value_index" representing the last character in the word instead.
        if len(interpretation.spaced_by) > 0:
            # print("interpretation is spaced")
            all_words = Content.objects.all().filter(interpretation_id_id=iid,
                                                     audio_id_id=aid).order_by('value_index')
            word_index = 0
            word_lengths_dict = {}
            summing_length = 0
            # print(all_words[0].audio_time)
            while word_index < len(all_words):
                if all_words[word_index].audio_time is not None:  # if it has a timestamp, then
                    # print(all_words[word_index].value, len(all_words[word_index].value))   # print the word and the length of the word
                    # print(all_words[word_index].value_index, all_words[word_index].audio_time)   # print the word's index # and the timestamp
                    # add an entry to the dictionary key: word's index and then value: [starting character of word, ending char of word]
                    word_lengths_dict[all_words[word_index].value_index] = [
                        summing_length, summing_length-1+len(all_words[word_index].value)]
                if word_index > 0:
                    if all_words[word_index].value == "\n" and all_words[word_index-1].value == "\n":
                        summing_length += 1
                    elif all_words[word_index].value == "\n" and not all_words[word_index-1].value == "\n":
                        summing_length += 0
                    else:
                        summing_length += len(all_words[word_index].value) + 1
                elif word_index == 0:
                    if all_words[word_index].value == "\n":
                        summing_length += 1
                    else:
                        summing_length += len(all_words[word_index].value) + 1

                # print(all_words[word_index].value)
                # print(summing_length)  # should be starting character of the next word
                word_index += 1
            # print(word_lengths_dict)
        # this already works if the language is not spaced

        # print("else")
        m = 0
        while m < len(query):
            obj = query[m]
            # print(obj)
            associations_times.append(obj.audio_time)
            associations_chars.append(obj.value_index)
            # if obj.audio_offset > 0:
            associations_offsets.append(obj.audio_offset)
            # else:
            #     associations_offsets.append(45)
            m += 1

        # print("next three")
        # print(associations_times)
        # print(associations_chars)
        # print(associations_offsets)

        if len(interpretation.spaced_by) > 0:
            new_array_times = []
            new_array_chars = []
            new_array_offsets = []
            # use word_lengths_dict to populate associations_times and associations_chars
            w = 0
            while w < len(associations_times) and w < len(associations_chars):

                # print(word_lengths_dict[associations_chars[w]])
                # print(associations_times[w])
                # new_array_chars.append(word_lengths_dict[associations_chars[w]][0])
                # new_array_chars.append(word_lengths_dict[associations_chars[w]][1])
                # new_array_times.append(associations_times[w]-associations_offsets[w]) # HERE
                # new_array_times.append(associations_times[w]+associations_offsets[w]) # HERE
                new_array_chars.append(
                    word_lengths_dict[associations_chars[w]][0])
                new_array_chars.append(
                    word_lengths_dict[associations_chars[w]][1])
                new_array_times.append(associations_times[w])  # HERE
                new_array_times.append(associations_times[w])  # HERE
                new_array_offsets.append(associations_offsets[w])
                new_array_offsets.append(associations_offsets[w])
                w += 1
            associations_times = new_array_times
            associations_chars = new_array_chars
            associations_offsets = new_array_offsets
        else:
            # double associations_times and associations_chars
            f = len(associations_times)-1
            for b in range(f+1):
                # print(f,b)
                # associations_times[f-b]-=associations_offsets[f-b]
                # associations_times.insert(f-b, associations_times[f-b]+associations_offsets[f-b]+associations_offsets[f-b]) # HERE
                # associations_chars.insert(f-b, associations_chars[f-b])
                associations_times.insert(f-b, associations_times[f-b])  # HERE
                associations_chars.insert(f-b, associations_chars[f-b])
                associations_offsets.insert(f-b, associations_offsets[f-b])
                b += 1

        # print(associations_times)
        # print(associations_chars)
        # print(associations_offsets)
        associations = {}
        associations_chars_new = []
        associations_times_new = []
        associations_offsets_new = []
        parentarray_times = []
        parentarray_chars = []
        parentarray_offsets = []
        parentarray_times.append(associations_times)
        parentarray_chars.append(associations_chars)
        parentarray_offsets.append(associations_offsets)
        # print("timestep: ", timestep)
        # print(parentarray_times)
        # print(parentarray_chars)

        while parentarray_times:
            if max(parentarray_times[0])-min(parentarray_times[0]) > a:
                times_differences = []
                j = 0
                while j < len(parentarray_times[0]) - 1 and j < len(parentarray_chars[0]) - 1:
                    times_differences.append(
                        parentarray_times[0][j+1]-parentarray_times[0][j])
                    j += 1
                    # print(j)
                # print(times_differences)
                difference_index = times_differences.index(
                    max(times_differences))
                associations_times_new = parentarray_times[0][:difference_index+1]
                associations_chars_new = parentarray_chars[0][:difference_index+1]
                associations_offsets_new = parentarray_offsets[0][:difference_index+1]
                parentarray_times[0] = parentarray_times[0][difference_index+1:]
                parentarray_chars[0] = parentarray_chars[0][difference_index+1:]
                parentarray_offsets[0] = parentarray_offsets[0][difference_index+1:]
                parentarray_times.insert(0, associations_times_new)
                parentarray_chars.insert(0, associations_chars_new)
                parentarray_offsets.insert(0, associations_offsets_new)
            elif max(parentarray_times[0])-min(parentarray_times[0]) <= a:
                entry = str(
                    min(parentarray_chars[0]))+"-"+str(max(parentarray_chars[0]))
                # print(entry)
                # print(parentarray_times[0])
                # if str(min(parentarray_times[0])) == str(max(parentarray_times[0])):
                # print("pause")
                # print("times: ", parentarray_times[0])
                # print("chars: ", parentarray_chars[0])
                # print("offsets: ", parentarray_offsets[0])
                mintimes = []
                maxtimes = []
                for x in range(len(parentarray_times[0])):
                    mintimes.append(
                        parentarray_times[0][x]-parentarray_offsets[0][x])
                    maxtimes.append(
                        parentarray_times[0][x]+parentarray_offsets[0][x])
                # unique_audio_times=[]
                # unique_audio_offsets=[]
                # for x in range(len(parentarray_times[0])-1):
                #     if not parentarray_times[0][x]==parentarray_times[0][x+1]:
                #         unique_audio_times.append(parentarray_times[0][x+1])
                #         unique_audio_offsets.append(parentarray_offsets[0][x+1])
                # if len(unique_audio_times)==1:
                #     parentarray_times[0][0] -= parentarray_offsets[0][0]
                #     parentarray_times[0][len(parentarray_times[0])-1] += parentarray_offsets[0][0]
                associations[str(min(mintimes))+"-" +
                             str(max(maxtimes))] = [entry]
                # associations[str(min(parentarray_chars[0]))+"-"+str(max(parentarray_chars[0]))].append(entry)
                parentarray_times.pop(0)
                parentarray_chars.pop(0)
                parentarray_offsets.pop(0)
        # print(associations)

        return JsonResponse({"associations": associations}, json_dumps_params={'ensure_ascii': False})

    def update(self, request, aid, iid):  # UPDATED 6/9/22 BY SKYSNOLIMIT08 TO WORK

        try:
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

        # print(request.data['associations'])
        if not Interpretation.objects.prefetch_related('shared_editors', 'created_by', 'audio_ID').filter(Q(audio_ID_id=aid, id=iid)).filter((Q(public=True) & Q(archived=False))
                                                                                                                                             | (Q(shared_editors=uid) & Q(archived=False)) | Q(created_by_id=uid)):
            return HttpResponse(status=404)

        query = Content.objects.all().prefetch_related('interpretation_id').filter(
            interpretation_id_id=iid).order_by('value_index')

        changed = []
        # print(association_dict)

        serializer = ContentSerializer(query, many=True)

        try:
            new_offset = request.data['offset']
            print(request.data['duration'])
            for entry in query:
                print(entry.audio_time)
                print(new_offset)
                if isinstance(entry.audio_time, int):
                    if (entry.audio_time+new_offset+entry.audio_offset) < (request.data['duration']/10) and (entry.audio_time+new_offset-entry.audio_offset) > 0:
                        query[entry.value_index].audio_time += new_offset

                        changed.append(query[entry.value_index])
                    else:
                        return HttpResponse(status=400)

            Content.objects.bulk_update(changed, ['audio_time'])
            return HttpResponse(status=200)
        except:
            association_dict = request.data['associations']

            # for some reason, the later line "query[key].audio_time = association_dict[key]" won't work without this line, even though indices_array is never referenced.  Is this a bug?
            indices_array = [entry['value_index'] for entry in serializer.data]

            # make sure the keys in the dict are integers
            # print(association_dict)
            association_dict = {int(k): v for k, v in association_dict.items()}
            # print(association_dict)
            # print(serializer.data)
            # old_values=[]
            for key in association_dict:
                if key >= 0:
                    # print(key)
                    # print(association_dict[key])
                    # print(query[key].audio_time)
                    # print("association dict Object(key, value): " + str(key) + ", " + str(association_dict[key]))
                    # print("old values Object(value_index, value, audio_time): " + str(key) + ", " + query[key].value + ", " + str(query[key].audio_time))
                    # old_values.append(query[key].audio_time)
                    # try:
                    for subkey in association_dict[key]:
                        query[key].audio_time = subkey
                        query[key].audio_offset = association_dict[key][subkey]
                    # except:
                    #     query[key].audio_time = association_dict[key]
                    #     query[key].audio_offset = 0
                    # print("new values Object(value_index, value, audio_time, audio_offset): " + str(key) + ", " + query[key].value + ", " + str(query[key].audio_time) + ", " + str(query[key].audio_offset))
                    # print("why is this not updating", query[key].audio_time)
                    changed.append(query[key])
                    # print(query[key])
                    # print("new: char " + key + " time " + query[key])
                    # print(changed)
                    # print(old_values)
            # print(changed[0].__dict__)
            # old_values_unique=[*set(old_values)]
            # # print(old_values_unique)
            # old_audio_times=[]
            # for key in query:
            #     old_audio_times.append(key.audio_time)
            # for l in old_values_unique:
            #     indices = [i for i, x in enumerate(old_audio_times) if x == l]
            #     for index in indices:
            #         query[index].audio_time = None
            #         query[index].audio_offset = None
            #         changed.append(query[index])
            # print(changed)
            # for oldvalue in old_values:
            #     indices = [i for i, x in enumerate(query) if x == "whatever"]
            #     print("key by value: ", key)
            # SOMETHING IS BROKEN IN HERE
            Content.objects.bulk_update(
                changed, ['audio_time', 'audio_offset'])

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
        # print("data", data)
        try:
            # print(request.headers)
            decoded_token = auth.verify_id_token(
                request.headers['Authorization'])
            uid = decoded_token['uid']
        except:
            return JsonResponse({'error': 'Firebase authentication failed'}, status=status.HTTP_400_BAD_REQUEST)

        # check if object already exists - create should only work if there isn't already an extended_user for uid
        if Extended_User.objects.filter(user_ID=uid).exists():
            user = Extended_User.objects.get(
                Q(user_ID=uid) | Q(email=data['email']))
            if user:
                return JsonResponse({'error': 'user already exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            obj = Extended_User(user_ID=uid,
                                description=data['description'],
                                display_name=data['display_name'],
                                anonymous=data['anonymous'],
                                email=data['email'])

            obj.save()
            serializer = self.serializer_class(obj)
            return Response({'user created'})

    # def update(self, request):
    #     data = request.data

    #     try:
    #         decoded_token = auth.verify_id_token(
    #             request.headers['Authorization'])
    #         uid = decoded_token['uid']
    #         user = Extended_User.objects.get(user_ID=uid)
    #         assert(user)
    #     except:
    #         # print("bad")
    #         return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

    #     user.description = data['description']
    #     user.display_name = data['display_name']
    #     user.anonymous = data['anonymous']
    #     user.save()
    #     serializer = self.serializer_class(user)
    #     return JsonResponse({"user": serializer.data})

    # def retrieve(self, request):
    #     data = request.data

    #     try:
    #         decoded_token = auth.verify_id_token(
    #             request.headers['Authorization'])
    #         uid = decoded_token['uid']
    #         user = Extended_User.objects.get(user_ID=uid)
    #         # assert(user)
    #     except:
    #         return JsonResponse({'error': 'Firebase authentication failed'}, status=status.HTTP_400_BAD_REQUEST)

    #     # if user.archived:
    #     #     return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
    #     serializer = self.serializer_class(user)
    #     return JsonResponse(serializer.data)
