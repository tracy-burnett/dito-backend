from django.urls import include, path
from rest_framework import routers
from storybooks.views import *

router = routers.SimpleRouter()
router.register(r'user', UserViewSet)
router.register(r'storybooks', AudioViewSet)
router.register(r'storybooks/{pk}/stories', StoryViewSet)
router.register(r'translations', TranslationViewSet)

urlpatterns = [
    path('', include(router.urls))
]