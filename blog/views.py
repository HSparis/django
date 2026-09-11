from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return render(request, "blog/home.html", {"title": "Home Page"})

def about(request):
    return render(request, "blog/about.html", {"title": "About Us", "team": "DjangoBlog Team"})

def contact(request):
    return render(request, "blog/contact.html", {"title": "Contact Us", "email": "contact@gabu.com"})

def base(request):
    return render(request, "blog/base.html", {"title": "Base Template"})