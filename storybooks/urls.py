from django.urls import include, path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from storybooks.views import *

router = routers.SimpleRouter()
router.register(r'user', UserViewSet)
router.register(r'audio', AudioViewSet)
#router.register(r'storybooks/{pk}/stories', StoryViewSet)
#router.register(r'audio/{pk}/translations', TranslationViewSet)
router.register(r'languages', LanguageViewSet)



presignedposturl_detail = UploadFileViewSet.as_view({
    'post': 'presignedposturl'
})

presignedgeturl_detail = DownloadFileViewSet.as_view({
    'post': 'presignedgeturl'
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
    path('audio/<int:aid>/translations/<int:lid>/', translations_detail, name='translations-detail'),
    path('audio/<int:aid>/translations/', translations_list, name='translations-list'),
    path('audio/<int:aid>/translations/<int:lid>/associations', associations_detail, name='associations-detail'),
    path('s3/presignedposturl', presignedposturl_detail, name='presignedposturl-detail'),
    path('s3/presignedgeturl', presignedgeturl_detail, name='presignedgeturl-detail')
]))
