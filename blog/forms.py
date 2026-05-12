from django import forms
from django.contrib.auth.models import User
from .models import Comment, Post
from django.contrib.auth.forms import UserCreationForm



class UserRegistrationForm(UserCreationForm):
    # Make email field required, in User model email field have optinal blank=true
    email = forms.EmailField(required=True, label='Email') 
    class Meta:
        model = User
        fields=("username", "email", "password1", "password2") 



class CommentModel(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["user_name", "user_email", "text"]
        labels = {
            "user_name": "Your Name",
            "user_email": "Your Email",
            "text": "Your Comment"
        }

class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ["user", "slug", "date",]

