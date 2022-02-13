from django import forms

from .models import Comment


class comment(forms.ModelForm):
    """create comment form"""
    text = forms.CharField()

    class Meta:
        model = Comment
        fields = ('text', )
