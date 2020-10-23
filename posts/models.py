from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User



class Post(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.ManyToManyField(User,default=1)
    post_id = models.CharField(max_length=64,unique=True)
    content = models.TextField()
    link = models.CharField(max_length=250,unique=True)
    created_on = models.DateField(auto_now_add=True)
    author_photo = models.CharField(max_length=150)
    author_screen_name = models.CharField(max_length=64)
    author_name = models.CharField(max_length=64)
    author_describtion = models.CharField(max_length=250)
    title = models.CharField(max_length=250,default='title')
    thumnail_photo = models.CharField(max_length=150,default='<img class="img rounded img-raised" src="threader.com:8000/static/assets/img/bg27.jpg"> height="300" width="400"')
    likes = models.ManyToManyField(User,blank=True,related_name='post_likes')
    dislikes =models.ManyToManyField(User,blank=True,related_name='post_dislikes')


    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name='post')
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user')
    text = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.post.title