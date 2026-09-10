from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return HttpResponse("<h1>Welcome to DjangoBlog</h1>")

def about(request):
    return render(request, "blog/about.html", {"team": "DjangoBlog Team"})