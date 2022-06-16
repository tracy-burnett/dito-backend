from django.urls import include, path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from storybooks.views import *

router = routers.SimpleRouter()
# router.register(r'user', ExtendedUserViewSet, basename="user")
# router.register(r'audio', AudioViewSet)
#router.register(r'storybooks/{pk}/stories', StoryViewSet)
#router.register(r'audio/{pk}/translations', TranslationViewSet)
# router.register(r'languages', LanguageViewSet)
#router.register(r'interpretation', InterpretationViewSet)


presignedposturl_detail = UploadFileViewSet.as_view({
    'post': 'presignedposturl' # has auth.  working 6/13/22.
})

presignedgeturl_detail = DownloadFileViewSet.as_view({
    'post': 'presignedgeturl'  # has auth.  working 6/13/22.
})

audio_list = AudioViewSet.as_view({
    'post':'create',             # has auth.  working 6/13/22.
    'get':'retrieve_public'      # no auth required.  working 6/14/22.
})

audio_update_owner = AudioViewSet.as_view({
    'patch':'partial_update_owner'    # has auth. working 6/13/22.
})

audio_update_editor = AudioViewSet.as_view({
    'patch':'partial_update_editor'        # has auth.  working 6/13/22.
})

audio_retrieve_private_user = AudioViewSet.as_view({
    'get':'retrieve_private_user'  # has auth.  working 6/13/22.
})

audio_retrieve_public_user = AudioViewSet.as_view({
    'get':'retrieve_public_user'      # NOT UPDATED YET.    [ignore for now?]
})


interpretations_detail = InterpretationViewSet.as_view({
    'post': 'create',                    # has auth.  working 6/13/22.
    'get': 'retrieve_audios',            # has auth.  working 6/13/22.
})

interpretations_editor = InterpretationViewSet.as_view({
    'patch': 'update_editors',          # has auth.  working 6/16/22.
    'get': 'retrieve_editors',          # NOT UPDATED YET.
})

interpretations_owner = InterpretationViewSet.as_view({
    'patch': 'update_owners',       # has auth.  working 6/16/22.
    'get': 'retrieve_owners',         # has auth.  working 6/13/22.
    'delete': 'destroy',               # NOT UPDATED YET.          (delete an interpretation that you created.)  [ignore for now]
})

interpretations = InterpretationViewSet.as_view({
    'get': 'retrieve_all'            # NOT UPDATED YET.   (see all interpretations that you have access to.)
})

interpretations_user = InterpretationViewSet.as_view({
    'get': 'retrieve_user'            # NOT UPDATED YET.  (see all public interpretations created by a particular user, not you.)
})

associations_detail = AssociationViewSet.as_view({
    'get': 'retrieve',       # NO AUTH REQUIRED.  working 6/13/22.
    'post': 'update'         # has auth.  working 6/13/22.
})

extended_user_details = ExtendedUserViewSet.as_view({
    'get': 'retrieve',            # has auth.  working 6/13/22.
    'post': 'create',             # has auth.  working 6/13/22.
    'patch': 'update'             # NOT UPDATED YET.      (update your user profile.)
})


# translations_detail = TranslationViewSet.as_view({
#     'post': 'create',
#     'patch': 'update',
#     'get': 'retrieve',
#     'delete': 'destroy'
# })
# translations_list = TranslationViewSet.as_view({
#     'get': 'list_languages'
# })



urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns.extend(format_suffix_patterns([
    path('audio/', audio_list, name='audio_list'),
    path('audio/<aid>/owner/', audio_update_owner, name='audio_update_owner'),
    path('audio/<aid>/editor/', audio_update_editor, name='audio_update_editor'),
    path('audio/user/', audio_retrieve_private_user, name='audio_retrieve_private_user'),
    path('audio/user/<int:uid>', audio_retrieve_public_user, name='audio_retrieve_public_user'),
    # path('audio/<aid>/translations/<int:lid>/', translations_detail, name='translations-detail'),
    # path('audio/<aid>/translations/', translations_list, name='translations-list'),
    path('content/<aid>/<iid>', associations_detail, name='associations-detail'),
    path('s3/presignedposturl', presignedposturl_detail, name='presignedposturl-detail'),
    path('s3/presignedgeturl', presignedgeturl_detail, name='presignedgeturl-detail'),
    path('interpretations/audio/<aid>/', interpretations_detail, name='interpretations_detail'),
    path('interpretations/<iid>/audio/<aid>/editor/', interpretations_editor, name='interpretations_editor'),    
    path('interpretations/<iid>/audio/<aid>/owner/', interpretations_owner, name='interpretations_owner'),
    path('interpretations/', interpretations, name='interpretations'),
    path('interpretations/user/<int:uid>/', interpretations_user, name='interpretations_user'),
    # path('user/<int:aid>/', extended_user_details, name='extended_user_details'),
    path('user/', extended_user_details, name='extended_user_details'),
]))
