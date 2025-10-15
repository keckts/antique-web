from django.shortcuts import render

# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash, get_user_model
from django.http import JsonResponse

from django.contrib.auth import logout
from .forms import LoginForm, SellerForm, SettingsForm, SignUpForm
import json


User = get_user_model()

# ------------------------------
# Authentication Views
# ------------------------------

def signup_view(request):
    """User signup view"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Explicitly set backend for login
            from django.contrib.auth import get_backends
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup_page.html', {'form': form})

from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return JsonResponse({"success": True, "redirect": "/dashboard/"})
        else:
            # Convert form.errors to a simple dict
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({"success": False, "errors": errors})
    else:
        form = AuthenticationForm()
    
    return render(request, "accounts/login_page.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('index')

def settings(request):
    settings_form = SettingsForm(instance=request.user)
    return render(request, 'accounts/settings/settings.html', {'form': settings_form})

def seller_form(request):
    if request.method == "POST":
        form = SellerForm(request.POST)
        if form.is_valid():
            seller = form.save(commit=False)
            seller.user = request.user
            seller.save()
            return redirect('dashboard')
    else:
        form = SellerForm()
    return render(request, 'accounts/selling/seller_form.html', {'form': form})


def verify_password(request):
    if request.method == "POST":
        print("method post")
        password = request.POST.get("password", "")
        print(f"Password received: {password}")
        user = authenticate(username=request.user.username, password=password)
        return JsonResponse({"valid": user is not None})

    return JsonResponse({"error": "Invalid request method"}, status=400)

def reset_password(request):
    if request.method == "POST":
        data = json.loads(request.body)
        new_password = data.get("new_password", "")
        if new_password:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Keep the user logged in
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "New password not provided"})
    return JsonResponse({"error": "Invalid request method"}, status=400)
