from core import views
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social.apps.django_app.urls')),
    path('', include('posts.urls')),
    path('', include('users.urls')),
    path('', include('core.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
]

handler404 = views.handler404
handler500 = views.handler500
