from django.urls import include, path
from rest_framework import routers
from storybooks.views import *

router = routers.SimpleRouter()
router.register(r'user', UserViewSet)
router.register(r'audio', AudioViewSet)
router.register(r'storybooks/{pk}/stories', StoryViewSet)
router.register(r'audio/{<int:aid>}/translations/<int:lid>', TranslationViewSet)
router.register(r'languages', LanguageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]