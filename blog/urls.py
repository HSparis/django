from django.urls import path
from .views import PostListView, PostDetailView, about, contact

urlpatterns = [
    path("", PostListView.as_view(), name="home"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="post_detail"),
    path("about/", about, name="about"),
    path("contact/", contact, name="contact"),
]