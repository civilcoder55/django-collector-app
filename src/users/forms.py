from django import forms
from django.contrib.auth.forms import (PasswordChangeForm, SetPasswordForm,
                                       UserCreationForm)
from django.contrib.auth.models import User

from .models import Profile


class Register(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("email address already exists")
        else:
            return email


class Login(forms.Form):
    username = forms.CharField(required=True, error_messages={
                               'required': 'username field is required'})
    password = forms.CharField(required=True, error_messages={
                               'required': 'password field is required'})


class ActiveAuthDevice(forms.Form):
    code = forms.CharField(required=True, error_messages={
        'required': 'code field is required'})


class UpdateProfile(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)

    def clean_email(self):
        email = self.cleaned_data['email']
        if 'email' in self.changed_data:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("email address already exists")
            else:
                return email
        return email


class UpdatePass(PasswordChangeForm):
    pass


class UpdateAvatar(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']


class ResetPass(SetPasswordForm):
    pass


class ForgetPass(forms.Form):
    email = forms.CharField(required=True, error_messages={
        'required': 'email field is required'})
