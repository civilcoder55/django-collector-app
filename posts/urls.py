from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='blog'),
    path('home/', views.home, name='home'),
    path('posts/', views.my_posts, name='my_posts'),
    path('post/<int:id>', views.PostView.as_view(), name='post'),
    path('post/<int:id>/like', views.toggle_like, name='like'),
    path('post/<int:id>/dislike', views.toggle_dislike, name='dislike'),
    path('pdf/view/<int:id>', views.view_pdf, name='view_pdf'),
    path('pdf/download/<int:id>', views.download_pdf, name='download_pdf')
]
