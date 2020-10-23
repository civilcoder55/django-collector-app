from django.http import HttpResponse

from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.models import User
from social_core.pipeline.partial import partial
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice
def get_user_totp_device(user, confirmed=None):
    devices = devices_for_user(user, confirmed=confirmed)
    for device in devices:
        if isinstance(device, TOTPDevice):
            return device



@partial
def factor_auth(strategy, backend, user,request, details, *args, **kwargs):
    if user :
        device = get_user_totp_device(user)
        auth = strategy.session_get('auth', None)
        if not device == None and device.confirmed :
            if not auth:
                strategy.session['user_id'] = user.id
                return redirect(reverse("fa"))
            elif auth == True:
                strategy.session['auth'] = None
                return
        else:
            return 
    else :
        return 
