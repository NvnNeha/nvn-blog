from django.urls import path
from . import views

urlpatterns = [
    path('', views.starting_page, name="starting_page"),
    path('posts', views.all_posts, name="all_posts"),
    path('posts/<slug:slug>', views.detailed_post, name="detailed_post"),
    path('login/', views.user_login, name="user_login"),
    path('register/', views.user_register, name="user_register"),
    path("stored-posts/", views.stored_posts, name="stored_posts"),
    path("create-post/", views.create_post, name="create_post"),
    path("edit-post/<slug:slug>/", views.edit_post, name="edit_post"),
    path("delete-post/<slug:slug>/", views.delete_post, name="delete_post"),
]
