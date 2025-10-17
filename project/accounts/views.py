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

# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import EmailVerification
from .utils import generate_verification_code, send_verification_email
from django.utils import timezone
from datetime import timedelta
import json

@login_required
@require_POST
def send_verification_code_ajax(request):
    """Send a new verification code via AJAX"""
    try:
        code = generate_verification_code()
        
        # Update or create verification record
        verification, created = EmailVerification.objects.update_or_create(
            user=request.user,
            defaults={
                'code': code, 
                'created_at': timezone.now(),
                'verified': False
            }
        )
        
        # For testing: print to console
        print(f"Verification code for {request.user.email}: {code}")
        
        # Send email (comment out if not configured)
        try:
            send_verification_email(request.user, code)
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Verification code sent! Check your email and console.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error sending code: {str(e)}'
        }, status=500)

@login_required
@require_POST
def verify_email_ajax(request):
    """Verify email with code via AJAX"""
    try:
        input_code = request.POST.get('code', '').strip()
        
        if not input_code:
            return JsonResponse({
                'success': False,
                'message': 'Please enter a verification code.'
            })
        
        try:
            verification = EmailVerification.objects.get(
                user=request.user,
                verified=False
            )
            
            # Check expiry (30 minutes)
            expiry_time = verification.created_at + timedelta(minutes=30)
            if expiry_time < timezone.now():
                return JsonResponse({
                    'success': False,
                    'message': 'Code has expired. Please request a new one.'
                })
            
            # Verify code
            if verification.code == input_code:
                verification.verified = True
                verification.save()
                
                # Update user model if you have is_email_verified field
                request.user.is_email_verified = True
                request.user.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Email verified successfully! ✅'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid code. Please try again.'
                })
                
        except EmailVerification.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'No verification code found. Please request one.'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)

@login_required
@require_POST
def verify_password(request):
    """Verify user password via AJAX"""
    try:
        password = request.POST.get('password', '')
        
        if not password:
            return JsonResponse({
                'valid': False,
                'message': 'Please enter a password.'
            })
        
        # Check if password is correct
        is_valid = request.user.check_password(password)
        
        return JsonResponse({
            'valid': is_valid,
            'message': 'Password verified! ✅' if is_valid else 'Invalid password.'
        })
        
    except Exception as e:
        return JsonResponse({
            'valid': False,
            'message': f'Error: {str(e)}'
        }, status=500)