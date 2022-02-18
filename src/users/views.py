import base64
from io import BytesIO

import qrcode
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from social_django.models import UserSocialAuth
from utils.helpers import get_user_totp_device

from . import forms


class RegisterView(View):
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = forms.Register(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'])
            if user and user.is_active:
                login(request, user)
                return redirect('home')
        else:
            error = list(form.errors.as_data()[
                list(form.errors.as_data().keys())[0]][0])
            messages.error(request, error[0])
        return redirect('register')

    def get(self, request):
        return render(request, 'users/auth/register.html',
                      {'title': 'Register'})


class LoginView(View):
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('home')

        login_form = forms.Login(request.POST)
        if login_form.is_valid():
            user = authenticate(
                username=login_form.cleaned_data['username'],
                password=login_form.cleaned_data['password'])
            if user and user.is_active:
                device = get_user_totp_device(user)
                if device is not None and device.confirmed:
                    serializer = Serializer(settings.SECRET_KEY, 180)
                    token = serializer.dumps(
                        {'user_id': user.id}).decode('utf-8')
                    return render(request, 'users/auth/fa.html',
                                  {'title': '2fa', 'token': token})
                login(request, user)
                return redirect('home')
            messages.error(request, 'Username or Password is incorrect')

        else:
            error = list(login_form.errors.as_data()[
                list(login_form.errors.as_data().keys())[0]][0])
            messages.error(request, error[0])
        return redirect('login')

    def get(self, request):
        return render(request, 'users/auth/login.html',
                      {'title': 'Login'})


def second_auth(request):
    if request.method == 'POST':
        token = request.POST.get("token", "")
        code = request.POST.get("code", "")
        serializer = Serializer(settings.SECRET_KEY)
        try:
            data = serializer.loads(token)
            user_id = data['user_id']
            user = User.objects.filter(id=user_id).first()
            device = get_user_totp_device(user)
            if device.verify_token(code):
                login(request, user,
                      backend='django.contrib.auth.backends.ModelBackend')
                return redirect('home')
            else:
                raise
        except Exception:
            messages.error(request, 'please login again')
            return redirect('login')
    return HttpResponseForbidden()


def social_second_auth(request):
    user_id = request.session.get('user_id', None)
    if user_id:
        if request.method == 'POST':
            code = int(request.POST.get('code'))
            user = User.objects.filter(id=user_id).first()
            device = get_user_totp_device(user)
            if device.verify_token(code):
                request.session['auth'] = True
                return redirect(
                    reverse(
                        'social:complete',
                        kwargs={'backend': "twitter"}))
            else:
                messages.error(request, 'please login again')
        return render(request, 'users/auth/social_fa.html', {'title': '2fa'})
    return redirect('login')


@login_required
def log_out(request):
    logout(request)
    return redirect('home')


class ProfileView(LoginRequiredMixin, View):
    def post(self, request):
        info_form = forms.UpdateProfile(request.POST, instance=request.user)
        avatar_form = forms.UpdateAvatar(
            request.POST, request.FILES, instance=request.user.profile)
        if info_form.is_valid() and avatar_form.is_valid():
            info_form.save()
            avatar_form.save()
            messages.success(
                request, 'your information updated successfully')
        else:
            error = list(info_form.errors.as_data()[
                list(info_form.errors.as_data().keys())[0]][0])
            messages.error(request, error[0])

        return redirect('profile')

    def get(self, request):
        return render(request, 'users/profile/index.html',
                      {'title': 'My Profile'})


class PasswordView(LoginRequiredMixin, View):
    def post(self, request):
        password_form = forms.UpdatePass(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request, 'your password updated successfully')
        else:
            error = list(password_form.errors.as_data()[
                list(password_form.errors.as_data().keys())[0]][0])
            messages.error(request, error[0])
        return redirect('password')

    def get(self, request):
        return render(request, 'users/profile/password.html',
                      {'title': 'Change Password'})


@login_required
def social(request):
    social_user = UserSocialAuth.objects.filter(
        user_id=request.user.id).first()
    screen_name = social_user.extra_data['access_token']['screen_name']\
        if social_user else False
    return render(
        request, 'users/profile/social.html',
        {'title': 'Linked Accounts', 'socialuser': screen_name})


@login_required
def delete(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('home')
    return render(
        request, 'users/profile/delete.html',
        {'title': 'Delete My Account', })


@login_required
def tfa(request, format=None):
    device = get_user_totp_device(request.user)
    if not device:
        type = 'None'

    elif device is not None and not device.confirmed:
        type = 'None'
        device.delete()
    else:
        type = 'Activated'
    return render(request, 'users/profile/device.html',
                  {'title': 'Security', 'type': type})


class AuthActivationView(LoginRequiredMixin, View):
    def post(self, request):
        activation_form = forms.ActiveAuthDevice(request.POST)
        if activation_form.is_valid():
            code = activation_form.cleaned_data['code']
            device = get_user_totp_device(request.user)
            if device is not None and device.verify_token(code):
                if not device.confirmed:
                    device.confirmed = True
                    device.save()
                    return redirect('2fa')
            else:
                messages.error(request, 'invalid or expired code')
        else:
            error = list(activation_form.errors.as_data()[
                list(activation_form.errors.as_data().keys())[0]][0])
            messages.error(request, error[0])

        return redirect('2fa_activate')

    def get(self, request):
        device = get_user_totp_device(request.user)
        if device is not None and device.confirmed:
            return redirect('device')

        if not device:
            device = request.user.totpdevice_set.create(confirmed=False)

        authenticator_url = device.config_url
        qr_image = qrcode.make(authenticator_url)

        buffered = BytesIO()
        qr_image.save(buffered, format="JPEG")
        qr_image = base64.b64encode(buffered.getvalue())
        return render(request, 'users/profile/device.html',
                      {'title': 'Security',
                       'authenticator_url': authenticator_url,
                       'type': 'Require_Activation',
                       'qr_image': str(qr_image, "utf-8")})


class AuthDeActivationView(LoginRequiredMixin, View):
    def post(self, request):
        activation_form = forms.ActiveAuthDevice(request.POST)
        if activation_form.is_valid():
            code = activation_form.cleaned_data['code']
            device = get_user_totp_device(request.user)
            if device is not None and device.verify_token(code):
                device.delete()
                messages.success(request, 'device deleted successfully')
                return redirect('2fa')
            else:
                messages.error(request, 'invalid or expired code')
        else:
            error = list(activation_form.errors.as_data()[
                list(activation_form.errors.as_data().keys())[0]][0])
            messages.error(request, error[0])

        return redirect('2fa_deactivate')

    def get(self, request):
        device = get_user_totp_device(request.user)
        if device is None or not device.confirmed:
            return redirect('2fa')

        return render(request, 'users/profile/device.html',
                      {'title': 'Security', 'type': 'Delete'})


class ForgetPasswordView(View):
    def post(self, request):
        forget_form = forms.ForgetPass(request.POST)
        if forget_form.is_valid():
            email = forget_form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                print(uid, token)
            messages.success(
                request, 'Password reset link has beed sent to your email')
        else:
            error = list(forget_form.errors.as_data()[
                list(forget_form.errors.as_data().keys())[0]][0])
            messages.error(request, error[0])
        return redirect('forget_password')

    def get(self, request):
        return render(request, 'users/auth/forget.html',
                      {'title': 'Reset Password Request'})


class ResetPasswordView(View):
    def post(self, request, uid, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.filter(id=user_id).first()
            if default_token_generator.check_token(user, token):
                reset_form = forms.ResetPass(user, request.POST)
                if reset_form.is_valid():
                    reset_form.save()
                    messages.success(
                        request, 'your password updated successfully')
                    return redirect('login')
                else:
                    error = list(reset_form.errors.as_data()[
                        list(reset_form.errors.as_data().keys())[0]][0])
                    messages.error(request, error[0])
                    return redirect('reset_password', uid=uid, token=token)
            else:
                raise

        except Exception:
            messages.error(request, 'invalid or expired token')
            return redirect('forget_password')

    def get(self, request, uid, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.filter(id=user_id).first()
            if default_token_generator.check_token(user, token):
                return render(request, 'users/auth/reset.html',
                              {'title': 'Reset Password'})
            else:
                raise
        except Exception:
            messages.error(request, 'invalid or expired token')
            return redirect('forget_password')
