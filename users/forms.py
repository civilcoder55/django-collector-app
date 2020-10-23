from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm,SetPasswordForm
from .models import Profile
#----------------------------------------------------------------------------------------------------------------------------------------------#
class Register(UserCreationForm):
    first_name = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'class':"form__input",'placeholder':"First Name",'required':True}) )
    last_name = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'class':"form__input",'placeholder':"Last Name",'required':True}) )
    email = forms.EmailField(max_length=254,widget=forms.TextInput(attrs={'class':"form__input",'placeholder':"Email",'required':True}))
    username = forms.CharField(max_length=254,widget=forms.TextInput(attrs={'class':"form__input",'placeholder':"Username",'required':True}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':"form__input",'placeholder':"Password",'required':True}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':"form__input",'placeholder':"Confirm Password",'required':True}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists() :
            raise forms.ValidationError("Email address is already exsist")
        else:
            return email
#----------------------------------------------------------------------------------------------------------------------------------------------#
class Login(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : "form__input",'placeholder':"Username",'required':True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class' : "form__input",'placeholder':"Password",'required':True}))
#----------------------------------------------------------------------------------------------------------------------------------------------#
class TwoFactorAuth(forms.Form):
    token = forms.CharField(widget=forms.TextInput(attrs={'type':'hidden','required':True}))
    code = forms.CharField(widget=forms.NumberInput(attrs={'maxlength' : "6",'class' : "form__input",'placeholder':'Authentication code','required':True,'oninput':"javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);",}))
    def __init__(self, *args, **kwargs):
        initial_arguments = kwargs.get('initial', None)
        updated_initial = {}
        if initial_arguments:
            token = initial_arguments.get('token',None)
        else :
            token = None
        if token :
            updated_initial['token'] = token 
        kwargs.update(initial=updated_initial)
        super(TwoFactorAuth, self).__init__(*args, **kwargs)
#----------------------------------------------------------------------------------------------------------------------------------------------#
class ActiveTwoFactorAuth(forms.Form):
    code = forms.CharField(widget=forms.NumberInput(attrs={'maxlength' : "6",'class' : "form__input",'required':True,'oninput':"javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength);",}))
#----------------------------------------------------------------------------------------------------------------------------------------------#
class UpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'class' : "form__input form__input--margin",}) )
    last_name = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'class' : "form__input form__input--margin",}) )
    email = forms.EmailField(max_length=254,widget=forms.TextInput(attrs={'class' : "form__input form__input--margin",}))
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',  )

    def clean_email(self):
        email = self.cleaned_data['email']
        if 'email' in self.changed_data :
            if User.objects.filter(email=email).exists() :
                raise forms.ValidationError("Email address is already exsist")
            else:
                return email
        return email
#----------------------------------------------------------------------------------------------------------------------------------------------#
class UpdatePass(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class' : "form__input form__input--margin" ,'required':True}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class' : "form__input form__input--margin"  ,'required':True}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class' : "form__input form__input--margin"  ,'required':True}))
#----------------------------------------------------------------------------------------------------------------------------------------------#
class ResetPass(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':"form__input",'placeholder':"Password",'required':True}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':"form__input",'placeholder':"Confirm Password",'required':True}))
#----------------------------------------------------------------------------------------------------------------------------------------------#
class ProfileUpdateForm(forms.ModelForm):
    pic = forms.ImageField(widget=forms.FileInput(attrs={"class":'form__gallery-upload','id':'form__gallery-upload','data-name':"#gallery1"}),required = False)
    class Meta:
        model = Profile
        fields = ['pic']
#----------------------------------------------------------------------------------------------------------------------------------------------#  
class ResetPassRequest(forms.ModelForm):
    email = forms.CharField(widget=forms.TextInput(attrs={'class' : "form__input",'placeholder':"Email",'required':True}))
    class Meta:
        model = User
        fields = ('email', )
#----------------------------------------------------------------------------------------------------------------------------------------------#