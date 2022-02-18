from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('about', about, name='about'),
    path('in_use', inuse, name='inuse'),
    re_path(r'^media/(?P<path>.*)$', media)
]
