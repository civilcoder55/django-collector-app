from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile_pic')
    pic = models.ImageField(
        default='profile_pics/default.jpg', upload_to='profile_pics')

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.pic.path)

        if img.height > 100 or img.width > 100:
            output_size = (250, 250)
            img.thumbnail(output_size)
            img.save(self.pic.path)
