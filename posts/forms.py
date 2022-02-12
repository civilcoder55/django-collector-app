from django import forms

from .models import Comment


class comment(forms.ModelForm):
    """create comment form"""
    text = forms.CharField(widget=forms.Textarea(attrs={
                           'class': "form__textarea", 'placeholder': "Write your comment", 'required': True}))

    class Meta:
        model = Comment
        fields = ('text', )
