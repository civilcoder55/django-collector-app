import pdfkit
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Count
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

    posts = Post.objects.annotate(Count('post_comments')).all().values(
        'id', 'thumnail_photo', 'created_at', 'author_screen_name',
        'title', 'rtl', 'post_comments__count').order_by('-created_at')
    posts = paginate(objects=posts, page=page, objects_per_page=12)

    random_posts = cache.get(f'random_posts')
    if not random_posts:
        random_posts = Post.objects.all().values(
            'id', 'thumnail_photo', 'created_at', 'author_screen_name', 'rtl',
            'title').order_by('?')[:5]
        cache.set(f'random_posts', random_posts, timeout=60*15)

    context = {'title': 'Home', 'posts': posts, 'random_posts': random_posts}
    return render(request, 'main/index.html', context)


@login_required
def my_posts(request):
    page = request.GET.get('page', 1)

    posts = Post.objects.annotate(
        Count('post_comments')).filter(
        username=request.user.id).values(
        'id', 'thumnail_photo', 'created_at', 'author_screen_name', 'title',
        'post_comments__count').order_by('-created_at')

    posts = paginate(objects=posts, page=page, objects_per_page=12)

    return render(request, 'posts/my_posts.html',
                  {'title': 'My Posts', 'posts': posts})


@login_required
def toggle_like(request, id):
    post = Post.objects.filter(id=id).first()
    if post and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        user_like = post.likes.filter(username=request.user.username).exists()
        user_dislike = post.dislikes.filter(
            username=request.user.username).exists()
        if user_like:
            post.likes.remove(request.user.id)
            user_like = False
        elif user_dislike:
            post.dislikes.remove(request.user.id)
            user_dislike = False
            post.likes.add(request.user.id)
            user_like = True
        else:
            post.likes.add(request.user.id)
            user_like = True

        taste = {
            'post_likes': post.likes.count(),
            'post_dislikes': post.dislikes.count(),
            'user_like': user_like,
            'user_dislike': user_dislike
        }
        return JsonResponse(taste)
    return HttpResponseForbidden()


@login_required
def toggle_dislike(request, id):
    post = Post.objects.filter(id=id).first()
    if post and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        user_like = post.likes.filter(username=request.user.username).exists()
        user_dislike = post.dislikes.filter(
            username=request.user.username).exists()
        if user_like:
            post.likes.remove(request.user.id)
            user_like = False
            post.dislikes.add(request.user.id)
            user_dislike = True
        elif user_dislike:
            post.dislikes.remove(request.user.id)
            user_dislike = False
        else:
            post.dislikes.add(request.user.id)
            user_dislike = True

        taste = {
            'post_likes': post.likes.count(),
            'post_dislikes': post.dislikes.count(),
            'user_like': user_like,
            'user_dislike': user_dislike
        }
        return JsonResponse(taste)
    return HttpResponseForbidden()


class PostView(View):

    @login_required
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
                'user_like': post.likes.filter(
                    username=request.user.username).exists(),
                'user_dislike': post.dislikes.filter(
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
