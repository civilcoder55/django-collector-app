from django.urls import path

from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', log_out, name='logout'),
    path('second-auth/', second_auth, name='second_auth'),
    path('second-auth/social', social_second_auth, name='social_second_auth'),
    path('setting/profile', ProfileView.as_view(), name='profile'),
    path('setting/password', PasswordView.as_view(), name='password'),
    path('setting/social', social, name='social'),
    path('setting/delete', delete, name='delete'),
    path('setting/2fa', tfa, name='2fa'),
    path('setting/2fa/activate', AuthActivationView.as_view(), name='2fa_activate'),
    path('setting/2fa/deactivate', AuthDeActivationView.as_view(), name='2fa_deactivate'),
    path('forget-password', ForgetPasswordView.as_view(), name='forget_password'),
    path('reset/<uid>/<token>', ResetPasswordView.as_view(), name='reset_password'),
]
