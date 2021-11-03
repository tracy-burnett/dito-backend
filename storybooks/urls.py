from django.urls import path

from storybooks.views import *

urlpatterns = [
    path('', index, name='index'),
]