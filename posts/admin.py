from django.contrib import admin
from .models import Post,Comment


class CommentAdmin(admin.ModelAdmin):
    list_display=['post','user','text']
    
admin.site.register(Post)
admin.site.register(Comment,CommentAdmin)
