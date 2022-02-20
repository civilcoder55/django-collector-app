from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Post(models.Model):
    """Posts [twitter threads] model"""
    id = models.BigIntegerField(primary_key=True)
    username = models.ManyToManyField(User, default=1)
    title = models.CharField(max_length=250, default='title')
    content = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    author_photo = models.CharField(max_length=150)
    author_screen_name = models.CharField(max_length=64)
    author_name = models.CharField(max_length=64)
    author_describtion = models.CharField(max_length=250)
    rtl = models.BooleanField(default=True)
    thumnail_photo = models.CharField(max_length=150)
    likes = models.ManyToManyField(User, blank=True, related_name='post_likes')
    dislikes = models.ManyToManyField(
        User, blank=True, related_name='post_dislikes')

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Comments model"""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='post_comments')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_comments')
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.post.title
