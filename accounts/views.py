from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from .forms import UserRegisterForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, "You have been fully logged out from Kisan AI.")
        return redirect('home')
    return render(request, 'accounts/logout.html')
