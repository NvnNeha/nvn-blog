from django.contrib import admin
from .models import Post, Comment, Tag
# Register your models here.

class PostAdminForm(admin.ModelAdmin):
    prepopulated_fields = {"slug":("title",)}
    list_display=("title","user",)




admin.site.register(Post, PostAdminForm)
admin.site.register(Comment)
admin.site.register(Tag)

