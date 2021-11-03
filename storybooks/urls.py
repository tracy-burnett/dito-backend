from django.urls import include, path
from rest_framework import routers
from storybooks.views import *

router = routers.SimpleRouter()
router.register(r'', index)
router.register(r'user', UserViewSet)
router.register(r'storybooks', AudioListView)
router.register(r'storybooks/{pk}/stories', StoryViewSet)
router.register(r'translations', TranslationViewSet)

urlpatterns = [
    path('', include(router.urls))
]