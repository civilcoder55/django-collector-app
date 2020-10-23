from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse,HttpResponseForbidden,FileResponse,Http404
from django.urls import reverse
from django.shortcuts import render,redirect
from . import forms
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
import time
from social_django.models import UserSocialAuth
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator as s
from django.contrib.auth.models import User
import mimetypes
from pathlib import Path
from django.utils.http import http_date
from django.utils._os import safe_join
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.encoding import force_text ,force_bytes
from django.utils.http import urlsafe_base64_decode ,urlsafe_base64_encode
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
import os
import base64
#----------------------------------------------------------------------------------------------------------------------------------------------#
 # helper function to get secuirty decive of user
def get_user_totp_device(user, confirmed=None):
    devices = devices_for_user(user, confirmed=confirmed)
    for device in devices:
        if isinstance(device, TOTPDevice):
            return device
#----------------------------------------------------------------------------------------------------------------------------------------------#
def registe_r(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))
    form = forms.Register()
    if request.method == 'POST':
        form = forms.Register(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(username = form.cleaned_data['username'] , password=form.cleaned_data['password1'])
            if user and user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('home'))
        error = list(form.errors.as_data()[list(form.errors.as_data().keys())[0]][0])
        messages.error(request, error[0])
    return render(request , 'users/login/register.html' , {'signup' : form ,'title':'Register'})
#----------------------------------------------------------------------------------------------------------------------------------------------#
def log_in(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))
    form = forms.Login()
    if request.method == 'POST':
        form = forms.Login(request.POST)
        if form.is_valid():
            user = authenticate(username = form.cleaned_data['username'] , password=form.cleaned_data['password'])
            if user and user.is_active:
                device = get_user_totp_device(user)
                if device != None and device.confirmed :
                    s = Serializer(settings.SECRET_KEY, 180)
                    token = s.dumps({'user_id': user.id}).decode('utf-8')
                    form = forms.TwoFactorAuth(initial={'token':token})
                    return render(request , 'users/login/fa.html' , {'form' : form, 'title':'2fa' })
                login(request,user)
                return HttpResponseRedirect(reverse('home'))
            messages.error(request, 'Username or Password is incorrect')
            return render(request , 'users/login/login.html' , {'signin' : form , 'title':'Login'})
        error = list(form2.errors.as_data()[list(form2.errors.as_data().keys())[0]][0])
        messages.error(request, error[0])
        return redirect('login')
    return render(request , 'users/login/login.html' , {'signin' : form , 'title':'Login'})

#----------------------------------------------------------------------------------------------------------------------------------------------#
def two_factor_auth(request):
    if request.method == 'POST':
        form = forms.TwoFactorAuth(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            code = form.cleaned_data['code']
            # get user_id from token sent when tried to login
            s = Serializer(settings.SECRET_KEY)
            try:
                data= s.loads(token)
                user_id = data['user_id']
                user = User.objects.filter(id=user_id).first()
                # get secuirty device and try to verify the code 
                device = get_user_totp_device(user) 
                if device.verify_token(code):
                    login(request,user, backend='django.contrib.auth.backends.ModelBackend') # login the user if code is valid 
                    return HttpResponseRedirect(reverse('blog'))
                messages.error(request, '2FA code is wrong Please login again')
                return redirect('login')
            except Exception as e:
                messages.error(request, 'Timeout Please login again')
                return redirect('login')
        error = list(form.errors.as_data()[list(form.errors.as_data().keys())[0]][0])
        messages.error(request, error[0])
        return redirect('login')
    return HttpResponseForbidden()
#----------------------------------------------------------------------------------------------------------------------------------------------# 
def social_two_factor_auth(request):
    user_id = request.session.get('user_id',None)
    if user_id:
        if request.method == 'POST':
            code = int(request.POST.get('code'))
            user = User.objects.filter(id=user_id).first()
            device = get_user_totp_device(user)
            if code and user:
                if device.verify_token(code):
                    request.session['auth'] = True
                    return redirect(reverse('social:complete', kwargs={'backend':"twitter"}))
            messages.error(request, '2FA code is wrong Please try again')
            return render(request , 'users/login/social_fa.html' , {'title':'2fa' })
        return render(request , 'users/login/social_fa.html' , {'title':'2fa' })
    return redirect(reverse('login'))
#----------------------------------------------------------------------------------------------------------------------------------------------# 
@login_required    
def log_out(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))   
#----------------------------------------------------------------------------------------------------------------------------------------------# 
@login_required
def profile(request):
    if request.method == 'POST':
        info = forms.UpdateForm(request.POST,instance=request.user)
        pic = forms.ProfileUpdateForm(request.POST,request.FILES,instance=request.user.profile_pic) 
        if info.is_valid() and pic.is_valid():
            info.save()
            pic.save()
            messages.success(request, 'Your information was successfully updated!')
            return redirect ('profile')
        error = list(info.errors.as_data()[list(info.errors.as_data().keys())[0]][0])
        messages.error(request, error[0])
        return redirect ('profile')
    info = forms.UpdateForm(instance=request.user)
    pic = forms.ProfileUpdateForm(instance=request.user.profile_pic)
    return render(request,'users/profile/profile.html',{'title':'My Profile','info' : info ,'pic':pic })
#----------------------------------------------------------------------------------------------------------------------------------------------# 
@login_required 
def password(request):
    if request.method == 'POST':
        password = forms.UpdatePass(request.user, request.POST)
        if password.is_valid():
            user = password.save()
            update_session_auth_hash(request, user) 
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password')
        error = list(password.errors.as_data()[list(password.errors.as_data().keys())[0]][0])
        messages.error(request, error[0])
        return redirect('password')
    password = forms.UpdatePass(request.user)
    return render(request,'users/profile/password.html',{'title':'Change Password','password' : password })
#----------------------------------------------------------------------------------------------------------------------------------------------#
@login_required
def social(request):
    social_user = UserSocialAuth.objects.filter(user_id=request.user.id).first()
    screen_name = social_user.extra_data['access_token']['screen_name'] if social_user else False
    return render(request,'users/profile/social.html',{'title':'Linked Accounts','socialuser': screen_name}) 
#----------------------------------------------------------------------------------------------------------------------------------------------#
@login_required
def delete(request):
    if request.method == 'POST':
        request.user.delete()
        return HttpResponseRedirect(reverse('home'))
    return render(request,'users/profile/delete.html',{'title':'Delete My Account', }) 
#----------------------------------------------------------------------------------------------------------------------------------------------# 
@login_required
def device(request, format=None):
    device = get_user_totp_device(request.user)
    if not device :
        return render(request,'users/profile/device.html',{'title': 'Security','state':'None'})
    elif device != None and not device.confirmed :
        device.delete()
        return render(request,'users/profile/device.html',{'title': 'Security','state':'None'})
    
    return render(request,'users/profile/device.html',{'title': 'Security','state':'True'})
#----------------------------------------------------------------------------------------------------------------------------------------------# 
@login_required
def activate(request):
    device = get_user_totp_device(request.user)
    if device != None and device.confirmed :
        return redirect('device')
    if not device:
        device = user.totpdevice_set.create(confirmed=False)
    url = device.config_url
    img = qrcode.make(url)
    img.save('./media/qr.png')
    with open("./media/qr.png", "rb") as imageFile:
        img = base64.b64encode(imageFile.read())
    os.remove("./media/qr.png")
    form = forms.ActiveTwoFactorAuth()
    if request.method=='POST':
        form = forms.ActiveTwoFactorAuth(request.POST)
        if form.is_valid():
            token = form.cleaned_data['code']
            if device != None and device.verify_token(token):
                if not device.confirmed:
                    device.confirmed = True
                    device.save()
                    return render(request,'users/profile/device.html',{'title': 'Security','state':'True'})
            messages.error(request, 'That is an invalid or expired code')
            return render(request,'users/profile/device.html',{'title': 'Security','url':url,'state':'False','form':form,'img':str(img,"utf-8")})
    return render(request,'users/profile/device.html',{'title': 'Security','url':url,'state':'False','form':form,'img':str(img,"utf-8")})
#----------------------------------------------------------------------------------------------------------------------------------------------# 
@login_required
def deactivate(request):
    device = get_user_totp_device(request.user)
    if device == None or not device.confirmed :
        return redirect('device')
    form = forms.ActiveTwoFactorAuth()
    if request.method=='POST':
        form = forms.ActiveTwoFactorAuth(request.POST)
        if form.is_valid():
            token = form.cleaned_data['code']
            if device != None and device.verify_token(token):
                device.delete()
                messages.success(request, 'Your device is now deleted')
                return redirect('device')
            messages.error(request, 'That is an invalid or expired code')
            return render(request,'users/profile/device.html',{'title': 'Security','state':'Del','form':form})
        messages.error(request, 'Something is Wrong')
        return render(request,'users/profile/device.html',{'title': 'Security','state':'Del','form':form,})
    return render(request,'users/profile/device.html',{'title': 'Security','state':'Del','form':form,})
#----------------------------------------------------------------------------------------------------------------------------------------------# 
def reset_pass_request(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))
    form = forms.ResetPassRequest()
    if request.method == 'POST':
        form = forms.ResetPassRequest(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user :
                token = s.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                messages.success(request, 'Password reset link has beed sent to your email')
                return redirect('reset_request')
            
            messages.error(request, 'There is no account with this email')
            return redirect('reset_request')
        error = list(form.errors.as_data()[list(form.errors.as_data().keys())[0]][0])
        messages.error(request, error[0])
        return redirect('reset_request')
    return render(request,'users/login/reset_request.html',{'title':'Reset Password Request','form' : form })
#----------------------------------------------------------------------------------------------------------------------------------------------# 
def reset_password(request,uid,token):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))
    try:
        user_id = force_text(urlsafe_base64_decode(uid))
        user = User.objects.filter(id=user_id).first()
        if s.check_token(user,token) :
            form = forms.ResetPass(user)
            if request.method == 'POST':
                form = forms.ResetPass(user,request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Your password was successfully updated!')
                    return redirect('login')
                error = list(form.errors.as_data()[list(form.errors.as_data().keys())[0]][0])
                messages.error(request, error[0])
                return redirect('reset_password',uid=uid,token=token)
            return render(request,'users/login/reset.html',{'title':'Reset Password','form' : form })
        else :
            messages.error(request, 'That is an invalid or expired token')
            return redirect('reset_request')
    except Exception as e:
        messages.error(request, 'That is an invalid or expired token')
        return redirect('reset_request')
#----------------------------------------------------------------------------------------------------------------------------------------------# 
def about(request):    
    return render(request, 'main/about.html',{'title':'The Collector APP'})
#----------------------------------------------------------------------------------------------------------------------------------------------# 
def handler404(request,*args,**kwargs):
    return render(request, 'main/Error.html', {'title':'Page not found','head':'Not Found','status':'404'},status=404,)
#----------------------------------------------------------------------------------------------------------------------------------------------# 
def handler500(request,*args,**kwargs):
    return render(request, 'main/Error.html', {'title':'Server Error','head':'Server Error','status':'500'},status=500)
#----------------------------------------------------------------------------------------------------------------------------------------------# 
def inuse(request):
    return render(request, 'main/inuse.html', {'title':'Account is already in use ','status':'403'},)
#----------------------------------------------------------------------------------------------------------------------------------------------# 
def media(request,path):
    fullpath = Path(safe_join(settings.MEDIA_ROOT, path))
    statobj = fullpath.stat()
    content_type, encoding = mimetypes.guess_type(str(fullpath))
    content_type = content_type or 'application/octet-stream'
    response = FileResponse(fullpath.open('rb'), content_type=content_type)
    response["Last-Modified"] = http_date(statobj.st_mtime)
    if encoding:
        response["Content-Encoding"] = encoding
    return response










    
    















    




    












