from django.urls import include, path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from storybooks.views import *

router = routers.SimpleRouter()
router.register(r'user', UserViewSet)
#router.register(r'audio', AudioViewSet)
#router.register(r'storybooks/{pk}/stories', StoryViewSet)
#router.register(r'audio/{pk}/translations', TranslationViewSet)

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


translations_list = TranslationViewSet.as_view({
    'get': 'list_languages'
})
translations_detail = TranslationViewSet.as_view({
    'post': 'create',
    'patch': 'update',
    'get': 'retrieve',
    'delete': 'destroy'
})
associations_detail = AssociationViewSet.as_view({
    'get': 'retrieve',
    'post': 'update'
})

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns.extend(format_suffix_patterns([
    path('audio/', audio_list, name='audio_list'),
    path('audio/<int:aid>/owner/', audio_update_owner, name='audio_update_owner'),
    path('audio/<int:aid>/editor/', audio_update_editor, name='audio_update_editor'),
    path('audio/user/', audio_retrieve_private_user, name='audio_retrieve_private_user'),
    path('audio/user/<int:uid>', audio_retrieve_public_user, name='audio_retrieve_public_user'),
]))


urlpatterns.extend(format_suffix_patterns([
    path('audio/<int:aid>/translations/<int:lid>/', translations_detail, name='translations-detail'),
    path('audio/<int:aid>/translations/', translations_list, name='translations-list'),
    path('audio/<int:aid>/translations/<int:lid>/associations', associations_detail, name='associations-detail')
]))

