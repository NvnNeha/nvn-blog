from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect
from .models import Post,Comment,Tag
from django.contrib.auth import login, logout,authenticate
from django.contrib.auth.decorators import login_required
from .forms import CommentModel,CreatePostForm,UserRegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils.text import slugify
# Create your views here.

def starting_page(request):
    posts = Post.objects.all().order_by("-date")[:3]
    if request.method == "POST":
        logout(request)
    return render(request, "blog/starting_page.html", {"posts": posts})


def all_posts(request):
    posts = Post.objects.all().order_by("-date")
    return render(request, "blog/all_posts.html", {"posts": posts})


def detailed_post(request,slug):
    post = get_object_or_404(Post, slug=slug)
    stored_list = request.session.get("stored_list")
    if stored_list is not None:
        is_save_for_later = post.id in stored_list
    else:
        is_save_for_later = False 

    comment_form = CommentModel()
    if request.method == "POST":
        comment_form = CommentModel(request.POST)
        if comment_form.is_valid():
            wait =comment_form.save(commit=False)
            wait.post = post
            wait.save()
            return HttpResponseRedirect(reverse("detailed_post", args=[slug])) 
    return render(request, "blog/detailed_post.html", {
        "post": post, 
        "comment_form": comment_form,
        "post_tag": post.tags.all(),
        "comments": post.comments.all().order_by("-id"),
        "is_save_for_later" : is_save_for_later
        })


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                return render(request, "registration/login.html", {"form": form})                
    else:
        form = AuthenticationForm(request)          
    return render(request, "registration/login.html", {"form": form})  



def user_register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username = form.cleaned_data["username"],
                                            email = form.cleaned_data["email"],
                                            password = form.cleaned_data["password1"])
            user.save()
            login(request, user)
            return redirect("/")
    else:
        form = UserRegistrationForm()
    return render(request, "registration/register.html", {
        "form" : form,
    })

def stored_posts(request):
    if request.method == "POST":
        stored_list = request.session.get("stored_list")
        if stored_list is None:
            request.session["stored_list"] = []
            stored_list = request.session.get("stored_list")

        post_id = int(request.POST["post-id"])
            
        if post_id not in stored_list:
            stored_list.append(post_id)
        else:
            stored_list.remove(post_id)    
        request.session["stored_list"] = stored_list
        return redirect("/")

    if request.method == "GET":
        stored_list = request.session.get("stored_list")
        context = {}
        if stored_list is None or len(stored_list)==0:
            context["has_post"]= False
        else:
            context["has_post"]= True
            context["post_list"] = Post.objects.filter(id__in=stored_list)
        return render(request, "blog/stored_posts.html", context)
    

@login_required
def create_post(request):
    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES)
        if form.is_valid():
            wait = form.save(commit=False)
            wait.user = request.user
            wait.slug = slugify(form.cleaned_data["title"])
            wait.save()
            form.save_m2m()

            return redirect("starting_page")
    else:        
        form = CreatePostForm()
    return render(request, "blog/create_post.html", {"form":form })


@login_required
def edit_post(request, slug):
    post= get_object_or_404(Post, slug=slug, user=request.user)
    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            wait = form.save(commit=False)
            wait.user = request.user
            wait.slug = slugify(form.cleaned_data["title"])
            wait.save()
            form.save_m2m()
            return redirect("starting_page")
    else:
        form = CreatePostForm(instance=post)
    return render(request, "blog/edit_post.html", {"form":form})


@login_required
def delete_post(request, slug):
    post= get_object_or_404(Post, slug=slug, user=request.user)
    if request.method == "POST":
        post.delete()
        return redirect('starting_page')
    return render(request, "blog/delete_post.html", {"post": post})
