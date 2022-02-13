import pdfkit
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect, JsonResponse)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from utils.helpers import paginate

from . import forms
from .models import Comment, Post


def home(request):
    page = request.GET.get('page', 1)
    posts = cache.get(f'posts_${page}')  # grab posts from cache

    if not posts:
        # grap posts from database and apply pagination
        posts = Post.objects.prefetch_related(
            'post_comments').all().order_by('-id')
        posts = paginate(objects=posts, page=page, objects_per_page=12)
        cache.set(f'posts_${page}', posts, timeout=60*15)

    # shuffle random posts to show in top of home page
    random_posts = Post.objects.all().order_by('?')[:5]
    context = {'title': 'Home', 'posts': posts, 'random_posts': random_posts}
    return render(request, 'main/index.html', context)


@login_required
def my_posts(request):
    page = request.GET.get('page', 1)
    # grab user posts from cache
    posts = cache.get(f'posts_${page}_${request.user.username}')

    if not posts:  # or get them from database and cache it
        # grap user posts from database and apply pagination
        posts = Post.objects.prefetch_related(
            'post_comments').all().order_by('-id')
        posts = paginate(objects=posts, page=page, objects_per_page=12)
        cache.set(f'posts_${page}_${request.user.username}',
                  posts, timeout=60*15)

    return render(request, 'posts/my_posts.html',
                  {'title': 'My Posts', 'posts': posts})


@login_required
def toggle_like(request, id):
    post = Post.objects.filter(id=id).first()
    if post and request.is_ajax():
        if post.dislikes.filter(username=request.user.username).exists():
            post.dislikes.remove(request.user.id)
        post.likes.add(request.user.id) if not post.likes.filter(
            username=request.user.username).exists() else post.likes.remove(
            request.user.id)
        taste = taste = {
            'post_likes': post.likes.count(),
            'post_dislikes': post.dislikes.count(),
            'user_does_like': post.likes.filter(
                username=request.user.username).exists(),
            'user_does_dislike': post.dislikes.filter(
                username=request.user.username).exists()}
        return JsonResponse(taste)
    return HttpResponseForbidden()


@login_required
def toggle_dislike(request, id):
    post = Post.objects.filter(id=id).first()
    if post and request.is_ajax():
        if post.likes.filter(username=request.user.username).exists():
            post.likes.remove(request.user.id)
        post.dislikes.add(request.user.id) if not post.dislikes.filter(
            username=request.user.username).exists() else post.dislikes.remove(
            request.user.id)
        taste = taste = {
            'post_likes': post.likes.count(),
            'post_dislikes': post.dislikes.count(),
            'user_does_like': post.likes.filter(
                username=request.user.username).exists(),
            'user_does_dislike': post.dislikes.filter(
                username=request.user.username).exists()}
        return JsonResponse(taste)
    return HttpResponseForbidden()


class PostView(LoginRequiredMixin, View):
    def post(self, request, id):
        comment_form = forms.comment(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = Post.objects.filter(id=id).first()
            comment.user = request.user
            comment.save()
            return redirect('/post/'+str(id)+'#commentbox')

    def get(self, request, id):
        post = Post.objects.filter(id=id).first()
        if post:
            comments = Comment.objects.filter(post=post).order_by('created_at')
            taste = {
                'post_likes': post.likes.count(),
                'post_dislikes': post.dislikes.count(),
                'user_does_like': post.likes.filter(
                    username=request.user.username).exists(),
                'user_does_dislike': post.dislikes.filter(
                    username=request.user.username).exists()}
            return render(
                request, 'posts/post.html',
                {'title': post.title, 'post': post, 'comments': comments,
                 'taste': taste})
        return HttpResponseRedirect(reverse('home'))


def view_pdf(request, id):
    post = Post.objects.filter(id=id).first()
    if post:
        return render(
            request, 'posts/pdf.html',
            {'title': post.title, 'content': post.content, })
    return HttpResponseRedirect(reverse('home'))


def download_pdf(request, id):
    # get view_pdf path => /pdf/view/1221554458
    path = reverse('view_pdf', args=(id,))
    pdf = pdfkit.from_url(f'{settings.APP_URL}{path}', False)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{str(id)}.pdf"'
    return response
