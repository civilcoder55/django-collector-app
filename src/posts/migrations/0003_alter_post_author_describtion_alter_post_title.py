# Generated by Django 4.0.2 on 2022-02-21 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_post_rtl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='author_describtion',
            field=models.CharField(max_length=280),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(default='title', max_length=280),
        ),
    ]
