from django.urls import include, path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from storybooks.views import *

router = routers.SimpleRouter()
router.register(r'user', ExtendedUserViewSet, basename="user")
router.register(r'audio', AudioViewSet)
#router.register(r'storybooks/{pk}/stories', StoryViewSet)
#router.register(r'audio/{pk}/translations', TranslationViewSet)
router.register(r'languages', LanguageViewSet)
#router.register(r'interpretation', InterpretationViewSet)


presignedposturl_detail = UploadFileViewSet.as_view({
    'post': 'presignedposturl'
})

presignedgeturl_detail = DownloadFileViewSet.as_view({
    'post': 'presignedgeturl'
})

translations_list = TranslationViewSet.as_view({
    'get': 'list_languages'
})


audio_list = AudioViewSet.as_view({
    'post':'create',
    'get':'retrieve_public'
})

audio_update_owner = AudioViewSet.as_view({
    'patch':'partial_update_owner'
})

audio_update_editor = AudioViewSet.as_view({
    'patch':'partial_update_editor'
})

audio_retrieve_private_user = AudioViewSet.as_view({
    'get':'retrieve_private_user'
})

audio_retrieve_public_user = AudioViewSet.as_view({
    'get':'retrieve_public_user'
})

translations_detail = TranslationViewSet.as_view({
    'post': 'create',
    'patch': 'update',
    'get': 'retrieve',
    'delete': 'destroy'
})
translations_list = TranslationViewSet.as_view({
    'get': 'list_languages'
})

interpretations_detail = InterpretationViewSet.as_view({
    'post': 'create',
    'get': 'retrieve_audios',
})

interpretations_editor = InterpretationViewSet.as_view({
    'patch': 'update_editors',
    'get': 'retrieve_editors',
})

interpretations_owner = InterpretationViewSet.as_view({
    'patch': 'update_owners',
    'get': 'retrieve_owners',
    'delete': 'destroy',
})

interpretations = InterpretationViewSet.as_view({
    'get': 'retrieve_all'
})

interpretations_user = InterpretationViewSet.as_view({
    'get': 'retrieve_user'
})

associations_detail = AssociationViewSet.as_view({
    'get': 'retrieve',
    'post': 'update'
})

extended_user_details = ExtendedUserViewSet.as_view({
    'get': 'retrieve',
    'post': 'create',
    'patch': 'update'
})

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns.extend(format_suffix_patterns([
    path('storybooks/audio/', audio_list, name='audio_list'),
    path('storybooks/audio/<int:aid>/owner/', audio_update_owner, name='audio_update_owner'),
    path('storybooks/audio/<int:aid>/editor/', audio_update_editor, name='audio_update_editor'),
    path('storybooks/audio/user/', audio_retrieve_private_user, name='audio_retrieve_private_user'),
    path('storybooks/audio/user/<int:uid>', audio_retrieve_public_user, name='audio_retrieve_public_user'),
    path('audio/<int:aid>/translations/<int:lid>/', translations_detail, name='translations-detail'),
    path('audio/<int:aid>/translations/', translations_list, name='translations-list'),
    path('audio/<int:aid>/translations/<int:lid>/associations/', associations_detail, name='associations-detail'),
    path('s3/presignedposturl', presignedposturl_detail, name='presignedposturl-detail'),
    path('s3/presignedgeturl', presignedgeturl_detail, name='presignedgeturl-detail')
]))

urlpatterns.extend(format_suffix_patterns([
    path('storybooks/interpretations/audio/<int:aid>/', interpretations_detail, name='interpretations_detail'),
    path('storybooks/interpretations/<int:iid>/audio/<int:aid>/editor', interpretations_editor, name='interpretations_editor'),    
    path('storybooks/interpretations/<int:iid>/audio/<int:aid>/owner', interpretations_owner, name='interpretations_owner'),
    path('storybooks/interpretations/', interpretations, name='interpretations'),
    path('storybooks/interpretations/user/<int:uid>/', interpretations_user, name='interpretations_user')
]))

urlpatterns.extend(format_suffix_patterns([
    path('user/<int:aid>/', extended_user_details, name='extended_user_details'),
    path('user/', extended_user_details, name='extended_user_details'),
]))

