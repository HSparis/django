from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Post, Category
from django.urls import reverse_lazy
from django.db.models import Count, Q
from .forms import PostForm

class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "post_detail",
            kwargs={"slug": self.object.slug}
        )


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "post_detail",
            kwargs={"slug": self.object.slug}
        )
    
class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    paginate_by = 6

    def get_queryset(self):
        return (Post.objects.filter(status="published")
                .select_related("category").order_by("-created_at", "-pk"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.annotate(
            published_count=Count("posts", filter=Q(posts__status="published"))
        ).order_by("name")
        context["featured_post"] = context["paginator"].object_list.first()
        return context

class   PostDeleteView(DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("home")

    
class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(status="published").select_related("category").prefetch_related("tags")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related = (Post.objects.filter(status="published").exclude(pk=self.object.pk)
                   .select_related("category"))
        if self.object.category_id:
            related = related.filter(category_id=self.object.category_id)
        context["related_posts"] = related.order_by("-created_at", "-pk")[:3]
        return context
    
def about(request):
    return render(request, "blog/about.html", {"team": "Neo Tokyo"})

def contact(request):
    return render(request, "blog/contact.html")