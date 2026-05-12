from django.db import models
from django.core.validators import MinLengthValidator 
from django.contrib.auth.models import User

# Create your models here.

class Tag(models.Model):
    caption = models.CharField(max_length=20)

    def __str__(self):
        return self.caption



class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=150)
    excerpt = models.CharField(max_length=200)
    image = models.ImageField(upload_to="upload", null=True)
    date = models.DateField(auto_now=True)
    slug = models.SlugField(unique=True, db_index=True)
    content = models.TextField(validators=[MinLengthValidator(20)])
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title
    

class Comment(models.Model):
    user_name = models.CharField(max_length=150)
    user_email  = models.EmailField()
    text = models.TextField(max_length=400)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name= "comments") 

    def __str__(self):
        return self.user_name