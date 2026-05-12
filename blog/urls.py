from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="starting_page"),
    path("posts", views.AllPostsView.as_view(), name="all_posts"),
    path("posts/<slug:slug>", views.PostDetailView.as_view(), name="detailed_post"),
    path(
        "login/",
        LoginView.as_view(template_name="registration/login.html"),
        name="user_login",
    ),
    path("logout/", LogoutView.as_view(), name="user_logout"),
    path("register/", views.RegisterView.as_view(), name="user_register"),
    path("stored-posts/", views.StoredPostsView.as_view(), name="stored_posts"),
    path("create-post/", views.PostCreateView.as_view(), name="create_post"),
    path(
        "edit-post/<slug:slug>/", views.PostUpdateView.as_view(), name="edit_post"
    ),
    path(
        "delete-post/<slug:slug>/",
        views.PostDeleteView.as_view(),
        name="delete_post",
    ),
]
