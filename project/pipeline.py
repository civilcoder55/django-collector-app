from django.shortcuts import redirect
from django.urls import reverse
from social_core.pipeline.partial import partial
from utils.helpers import get_user_totp_device


@partial
def factor_auth(strategy, backend, user, request, details, *args, **kwargs):
    if user:
        device = get_user_totp_device(user)
        auth = strategy.session_get('auth', None)
        if device is not None and device.confirmed:
            if not auth:
                strategy.session['user_id'] = user.id
                return redirect(reverse("fa"))
            elif auth is True:
                strategy.session['auth'] = None
    return
