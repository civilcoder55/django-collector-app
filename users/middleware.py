from django.shortcuts import redirect
from social_core.exceptions import AuthAlreadyAssociated, AuthMissingParameter
from social_django.middleware import SocialAuthExceptionMiddleware
from django.contrib import messages


class TwitterAuthAlreadyAssociatedMiddleware(SocialAuthExceptionMiddleware):
    # Redirect users to desired-url when AuthAlreadyAssociated exception occurs
    def process_exception(self, request, exception):
        if isinstance(exception, AuthAlreadyAssociated):
            if request.backend.name == "twitter":
                message = "This account is already in use."
                if message in str(exception):
                    return redirect('inuse')


class TwitterAuthMissingParameterMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if isinstance(exception, AuthMissingParameter):
            if request.backend.name == "twitter":
                messages.error(request, "Invalid Request")
                return redirect('login')
