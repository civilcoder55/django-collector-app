from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse,HttpResponseForbidden
from django.urls import reverse
from django.shortcuts import render,redirect
from django.core.paginator import Paginator , EmptyPage, PageNotAnInteger
from django.db.models import Q
from . import forms
from .models import Post ,Comment
import time
import random
import pdfkit
import os
from django.core.cache import cache


#function take Model Objects , page_number , and number of elemnts per page and return paginator objects
def paginate(objects , page , objects_per_page):
    paginator = Paginator(objects, objects_per_page) 
    try:
        paginated_objects = paginator.page(page) 
    except PageNotAnInteger:
        paginated_objects = paginator.page(1)
    except EmptyPage:
        paginated_objects = paginator.page(paginator.num_pages)
    
    return paginated_objects
#----------------------------------------------------------------------------------------------------------------------------------------------#
def home(request):
    page = request.GET.get('page', 1)
    posts = cache.get(f'posts_${page}') # grab posts from cache 

    if not posts : # or get them from database and cache it 
        # grap posts from database and apply pagination 
        posts = Post.objects.prefetch_related('post_comments').all().order_by('-id') 
        posts = paginate(objects=posts,page=page,objects_per_page=12)
        cache.set(f'posts_${page}', posts, timeout=60*15)

    # shuffle random posts to show in top of home page 
    random_posts = Post.objects.all().order_by('?')[:5]
    context = {'title':'Home','posts':posts,'random_posts':random_posts}
    return render(request,'main/index.html',context)
#----------------------------------------------------------------------------------------------------------------------------------------------#
@login_required
def myposts(request):
    page = request.GET.get('page', 1)
    posts = cache.get(f'posts_${page}_${request.user.username}') # grab user posts from cache 
    
    if not posts : # or get them from database and cache it 
        # grap user posts from database and apply pagination 
        posts = Post.objects.prefetch_related('post_comments').all().order_by('-id') 
        posts = paginate(objects=posts,page=page,objects_per_page=12)
        cache.set(f'posts_${page}_${request.user.username}', posts, timeout=60*15)

    return render(request,'posts/myposts.html',{'title':'My Posts','posts':posts})

#----------------------------------------------------------------------------------------------------------------------------------------------#
@login_required
def toggle_like(request,id):
    post = Post.objects.filter(post_id=id).first()
    if post and request.is_ajax():
        if post.dislikes.filter(username=request.user.username).exists() : post.dislikes.remove(request.user.id) # remove dislike if user already dislike
        post.likes.add(request.user.id) if not post.likes.filter(username=request.user.username).exists() else post.likes.remove(request.user.id)  # add like if user never liked and remove it if he already liked before
        taste = taste = {
                'post_likes' : post.likes.count(),
                'post_dislikes' : post.dislikes.count() ,
                'user_does_like' : post.likes.filter(username=request.user.username).exists() ,
                'user_does_dislike' : post.dislikes.filter(username=request.user.username).exists()
            }
        return JsonResponse(taste)                                         
    return HttpResponseForbidden()
#----------------------------------------------------------------------------------------------------------------------------------------------#
@login_required
def toggle_dislike(request,id):
    post = Post.objects.filter(post_id=id).first()
    if post and request.is_ajax():
        if post.likes.filter(username=request.user.username).exists() : post.likes.remove(request.user.id) # remove like if user already like
        post.dislikes.add(request.user.id) if not post.dislikes.filter(username=request.user.username).exists() else post.dislikes.remove(request.user.id)  # add dislike if user never disliked and remove it if he already disliked before
        taste = taste = {
                'post_likes' : post.likes.count(),
                'post_dislikes' : post.dislikes.count() ,
                'user_does_like' : post.likes.filter(username=request.user.username).exists() ,
                'user_does_dislike' : post.dislikes.filter(username=request.user.username).exists()
            }
        return JsonResponse(taste)                                         
    return HttpResponseForbidden()

#----------------------------------------------------------------------------------------------------------------------------------------------#
def post(request,id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            comment_form = forms.comment(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = Post.objects.filter(post_id =id).first()
                comment.user =request.user
                comment.save()
                return redirect ('/thread/'+str(id)+'#commentbox')
    else:
        post = Post.objects.filter(post_id =id).first()
        if post :
            comments = Comment.objects.filter(post=post).order_by('created_on')
            comment_form = forms.comment()
            taste = {
                'post_likes' : post.likes.count(),
                'post_dislikes' : post.dislikes.count() ,
                'user_does_like' : post.likes.filter(username=request.user.username).exists() ,
                'user_does_dislike' : post.dislikes.filter(username=request.user.username).exists()
            }
            return render(request , 'posts/post.html' , {'title':post.title,'post':post,'comments':comments,'comment_form':comment_form,'taste':taste})
        return HttpResponseRedirect(reverse('home'))

    return HttpResponseForbidden() 
#----------------------------------------------------------------------------------------------------------------------------------------------#
def pdf(request,id):
    post = Post.objects.filter(post_id =id).first()
    if post :     
        return render(request , 'posts/pdf.html' , {'title':post.title, 'content' : post.content,})
    return HttpResponseRedirect(reverse('home'))
#----------------------------------------------------------------------------------------------------------------------------------------------#
def print_pdf(request,num):
    pdf = pdfkit.from_url('http://thecollect0rapp.com/pdf/'+str(num), False)
    response = HttpResponse(pdf,content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="'+ str(num)+'.pdf"'
    return response
#----------------------------------------------------------------------------------------------------------------------------------------------#









