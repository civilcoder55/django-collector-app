from django.urls import path, re_path

from . import views

urlpatterns = [
    path('register/', views.registe_r, name='register'),
    path('login/', views.log_in, name='login'),
    path('login/security/', views.two_factor_auth, name='security'),
    path('security/', views.social_two_factor_auth, name='security'),
    path('logout/', views.log_out, name='logout'),
    path('setting/profile', views.profile, name='profile'),
    path('setting/password', views.password, name='password'),
    path('setting/social', views.social, name='social'),
    path('setting/delete', views.delete, name='delete'),
    path('setting/device', views.device, name='device'),
    path('setting/activate', views.activate, name='activate'),
    path('setting/deactivate', views.deactivate, name='deactivate'),
    path('about', views.about, name='about'),
    path('in_use', views.inuse, name='inuse'),
    path('reset_request', views.reset_pass_request, name='reset_request'),
    path('reset/<uid>/<token>', views.reset_password, name='reset_password'),
    re_path(r'^media/(?P<path>.*)$', views.media),
]
