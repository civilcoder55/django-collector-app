from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='blog'),
    path('home/', views.home, name='home'),
    path('posts/', views.myposts, name='myposts'),
    path('thread/<int:id>', views.post, name='thread'),
    path('thread/<int:id>/like', views.toggle_like, name='like'),
    path('thread/<int:id>/dislike', views.toggle_dislike, name='dislike'),
    path('pdf/<int:num>', views.pdf, name='pdf'),
    path('printpdf/<int:num>', views.print_pdf, name='printpdf'),
]
