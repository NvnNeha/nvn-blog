from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from .forms import CommentForm, CreatePostForm, UserRegistrationForm
from .models import Post


def _unique_slug(base, *, exclude_pk=None):
    base = slugify(base) or "post"
    slug = base
    n = 2
    qs = Post.objects.all()
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    while qs.filter(slug=slug).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug


class HomeView(ListView):
    model = Post
    template_name = "blog/starting_page.html"
    context_object_name = "posts"

    def get_queryset(self):
        return Post.objects.all().order_by("-date")[:3]


class AllPostsView(ListView):
    model = Post
    template_name = "blog/all_posts.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        return Post.objects.all().order_by("-date")


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detailed_post.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        post = self.object
        stored_list = self.request.session.get("stored_list") or []
        ctx["is_save_for_later"] = post.id in stored_list
        ctx["post_tag"] = post.tags.all()
        ctx["comments"] = post.comments.all().order_by("-id")
        ctx["comment_form"] = kwargs.get("comment_form") or CommentForm()
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.save()
            return redirect("detailed_post", slug=self.object.slug)
        ctx = self.get_context_data(comment_form=form)
        return self.render_to_response(ctx)


class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("starting_page")

    def form_valid(self, form):
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
        )
        login(self.request, user)
        return redirect(self.success_url)


class StoredPostsView(View):
    template_name = "blog/stored_posts.html"

    def get(self, request):
        from django.shortcuts import render

        stored_list = request.session.get("stored_list") or []
        if not stored_list:
            return render(request, self.template_name, {"has_post": False})
        return render(
            request,
            self.template_name,
            {"has_post": True, "post_list": Post.objects.filter(id__in=stored_list)},
        )

    def post(self, request):
        stored_list = request.session.get("stored_list") or []
        try:
            post_id = int(request.POST.get("post-id", ""))
        except (TypeError, ValueError):
            return redirect("starting_page")
        if post_id in stored_list:
            stored_list.remove(post_id)
        else:
            stored_list.append(post_id)
        request.session["stored_list"] = stored_list
        return redirect(request.META.get("HTTP_REFERER") or reverse("starting_page"))


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = CreatePostForm
    template_name = "blog/create_post.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.slug = _unique_slug(form.cleaned_data["title"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("detailed_post", args=[self.object.slug])


class AuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.get_object().user_id == self.request.user.id


class PostUpdateView(AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = CreatePostForm
    template_name = "blog/edit_post.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.slug = _unique_slug(
            form.cleaned_data["title"], exclude_pk=self.object.pk
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("detailed_post", args=[self.object.slug])


class PostDeleteView(AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/delete_post.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("starting_page")
