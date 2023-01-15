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

audio_update_public = AudioViewSet.as_view({
    'patch':'partial_update_public'
})

audio_retrieve_private_user = AudioViewSet.as_view({
    'get':'retrieve_private_user'  # has auth.  working 6/13/22.
})


interpretations_detail = InterpretationViewSet.as_view({
    'post': 'create',                    # has auth.  working 6/13/22.
    'get': 'retrieve_audios',            # has auth.  working 6/13/22.
})

interpretations_editor = InterpretationViewSet.as_view({
    'patch': 'update_editors',          # has auth.  working 6/16/22.
    'get': 'retrieve_editors',          # has auth.  working 6/17/22.
})

interpretations_viewer = InterpretationViewSet.as_view({
    'get': 'retrieve_viewers',          # has auth.  working 6/17/22.
})

interpretations_owner = InterpretationViewSet.as_view({
    'patch': 'update_owners',       # has auth.  working 6/16/22.
    'get': 'retrieve_owners',         # has auth.  working 6/13/22.
})

interpretations = InterpretationViewSet.as_view({
    'get': 'retrieve_all'            # NOT UPDATED YET.   (see all interpretations that you have access to.)
})

associations_detail = AssociationViewSet.as_view({
    'post': 'update'         # has auth.  working 6/13/22.
})

associations_retrieve = AssociationViewSet.as_view({
    'get': 'retrieve',       # NO AUTH REQUIRED.  working 6/13/22.
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
    path('audio/<aid>/public/', audio_update_public, name='audio_update_public'),
    path('audio/user/', audio_retrieve_private_user, name='audio_retrieve_private_user'),
    # path('audio/<aid>/translations/<int:lid>/', translations_detail, name='translations-detail'),
    # path('audio/<aid>/translations/', translations_list, name='translations-list'),
    path('content/<aid>/<iid>', associations_detail, name='associations-detail'),
    path('content/<aid>/<iid>/<int:timestep>/', associations_retrieve, name='associations-retrieve'),
    path('s3/presignedposturl', presignedposturl_detail, name='presignedposturl-detail'),
    path('s3/presignedgeturl', presignedgeturl_detail, name='presignedgeturl-detail'),
    path('interpretations/audio/<aid>/', interpretations_detail, name='interpretations_detail'),
    path('interpretations/<iid>/audio/<aid>/editor/', interpretations_editor, name='interpretations_editor'),    
    path('interpretations/<iid>/audio/<aid>/owner/', interpretations_owner, name='interpretations_owner'),  
    path('interpretations/<iid>/audio/<aid>/viewer/', interpretations_viewer, name='interpretations_viewer'),
    path('interpretations/', interpretations, name='interpretations'),
    # path('user/<int:aid>/', extended_user_details, name='extended_user_details'),
    path('user/', extended_user_details, name='extended_user_details'),
]))
