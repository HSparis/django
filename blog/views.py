from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Post, Category
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PostForm, RegisterForm


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "blog/register.html"
    success_url = "/"

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
        messages.success(self.request, "Post published successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "post_detail",
            kwargs={"slug": self.object.slug}
        )


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def dispatch(self, request, *args, **kwargs):
        if (
            not request.user.is_authenticated
            or (
                request.user != self.get_object().author
                and not request.user.is_superuser
            )
        ):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            "post_detail",
            kwargs={"slug": self.object.slug}
        )


class PostDeleteView(DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        if (
            not request.user.is_authenticated
            or (
                request.user != self.get_object().author
                and not request.user.is_superuser
            )
        ):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    paginate_by = 6

    def get_queryset(self):
        queryset = (
            Post.objects.filter(status="published")
            .select_related("category")
            .order_by("-created_at", "-pk")
        )
        category_name = self.request.GET.get("category")
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.annotate(
            published_count=Count("posts", filter=Q(posts__status="published"))
        ).order_by("name")
        context["current_category"] = self.request.GET.get("category")
        context["featured_post"] = context["paginator"].object_list.first()
        return context


class MyPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "blog/my_posts.html"
    paginate_by = 6
    login_url = "login"

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by("-created_at", "-pk")


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        posts = Post.objects.filter(status="published")
        if self.request.user.is_authenticated:
            posts = Post.objects.filter(
                Q(status="published") | Q(author=self.request.user)
            )
        return posts.select_related("author", "category").prefetch_related("tags")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related = (Post.objects.filter(status="published").exclude(pk=self.object.pk)
                   .select_related("category"))
        if self.object.category_id:
            related = related.filter(category_id=self.object.category_id)
        context["related_posts"] = related.order_by("-created_at", "-pk")[:3]
        return context


def about(request):
    return render(request, "blog/about.html", {"team": "Neo Niigata"})


def contact(request):
    return render(request, "blog/contact.html")


def custom_403(request, exception=None):
    return render(request, "blog/403.html", status=403)


def custom_404(request, exception=None):
    return render(request, "404.html", status=404)


def custom_500(request):
    return render(request, "500.html", status=500)

