from django.urls import path, include
from django.contrib import admin
from users import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social.apps.django_app.urls')),
    path('', include('posts.urls')),
    path('', include('users.urls')),
]

handler404 = views.handler404
handler500 = views.handler500
