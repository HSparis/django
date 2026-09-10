from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomLoginForm

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            login(request, form.user_cache)
            return redirect('home')
    else:
        form = CustomLoginForm()

    return render(request, 'registration/login.html', {'form': form})

@login_required
def home(request):
    return render(request, 'home.html')