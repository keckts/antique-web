# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from decouple import config
import json
import secrets

from .forms import LoginForm, SellerForm, SettingsForm, SignUpForm
from .models import EmailVerification, PasswordReset
from .utils import generate_verification_code
from service.models import Subscriber

EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

User = get_user_model()


# ------------------------------
# Email Utility Functions
# ------------------------------

def send_email_helper(subject, html_message, recipient_email, plain_text_message=None):
    """
    Centralized email sending function using Gmail configuration.
    
    Args:
        subject: Email subject line
        html_message: HTML content of the email
        recipient_email: Recipient's email address
        plain_text_message: Optional plain text fallback message
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        send_mail(
            subject=subject,
            message=plain_text_message or "Please view this email in HTML format.",
            from_email=EMAIL_HOST_USER,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed to {recipient_email}: {e}")
        return False


def send_verification_email(user, code):
    """Send verification code email to user"""
    subject = "Verify Your Email Address"
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50;">Email Verification</h2>
                <p>Hello {user.username},</p>
                <p>Your verification code is:</p>
                <div style="background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; margin: 20px 0;">
                    {code}
                </div>
                <p>This code will expire in 30 minutes.</p>
                <p>If you didn't request this verification, please ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #666;">This is an automated message, please do not reply.</p>
            </div>
        </body>
    </html>
    """
    plain_text = f"Your verification code is: {code}\nThis code will expire in 30 minutes."
    
    return send_email_helper(subject, html_message, user.email, plain_text)


def send_password_reset_email(user, reset_url):
    """Send password reset email to user"""
    subject = "Password Reset Request"
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2196F3;">Password Reset</h2>
                <p>Hello {user.username},</p>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background-color: #2196F3; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
                </div>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666;">{reset_url}</p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request a password reset, please ignore this email and your password will remain unchanged.</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #666;">This is an automated message, please do not reply.</p>
            </div>
        </body>
    </html>
    """
    plain_text = f"Password reset link: {reset_url}\nThis link will expire in 1 hour."
    
    return send_email_helper(subject, html_message, user.email, plain_text)


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


def login_view(request):
    """User login view with AJAX support"""
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return JsonResponse({"success": True, "redirect": "/dashboard/"})
        else:
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({"success": False, "errors": errors})
    else:
        form = AuthenticationForm()
    
    return render(request, "accounts/login_page.html", {"form": form})


def logout_view(request):
    """User logout view"""
    logout(request)
    return redirect('index')


# ------------------------------
# User Settings & Profile Views
# ------------------------------

@login_required
def settings_view(request):
    """User settings page"""
    settings_form = SettingsForm(instance=request.user)
    is_email_subscribed = Subscriber.objects.filter(email=request.user.email).exists()

    return render(request, 'accounts/settings/settings.html', {
        'form': settings_form, 
        'is_email_subscribed': is_email_subscribed
    })


@login_required
def seller_form(request):
    """Seller registration form"""
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


# ------------------------------
# Email Verification Views
# ------------------------------

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
        
        # Print to console for testing
        print(f"Verification code for {request.user.email}: {code}")
        
        # Send email
        email_sent = send_verification_email(request.user, code)
        
        if email_sent:
            message = 'Verification code sent! Check your email.'
        else:
            message = 'Verification code generated but email failed to send. Check console.'
        
        return JsonResponse({
            'success': True,
            'message': message
        })
    except Exception as e:
        print(f"Error in send_verification_code_ajax: {e}")
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
                if hasattr(request.user, 'is_email_verified'):
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
        print(f"Error in verify_email_ajax: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


# ------------------------------
# Password Management Views
# ------------------------------

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
        
        is_valid = request.user.check_password(password)
        
        return JsonResponse({
            'valid': is_valid,
            'message': 'Password verified! ✅' if is_valid else 'Invalid password.'
        })
        
    except Exception as e:
        print(f"Error in verify_password: {e}")
        return JsonResponse({
            'valid': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@login_required
@require_POST
def reset_password(request):
    """Reset password for logged-in user"""
    try:
        data = json.loads(request.body)
        new_password = data.get("new_password", "")
        
        if not new_password:
            return JsonResponse({
                "success": False, 
                "error": "New password not provided"
            })
        
        if len(new_password) < 8:
            return JsonResponse({
                "success": False,
                "error": "Password must be at least 8 characters long"
            })
        
        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)  # Keep user logged in
        
        return JsonResponse({"success": True})
        
    except json.JSONDecodeError:
        print("Error decoding JSON in reset_password")
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON data"
        }, status=400)
    except Exception as e:
        print(f"Error in reset_password: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@require_POST
def request_password_reset(request):
    """Handle password reset request via AJAX"""
    try:
        email = request.POST.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'Please enter your email address.'
            })
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Return success even if user doesn't exist for security
            return JsonResponse({
                'success': True,
                'message': 'If an account with this email exists, a password reset link will be sent.'
            })
        
        # Check rate limiting (60 seconds)
        recent_request = PasswordReset.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(seconds=60)
        ).first()
        
        if recent_request:
            time_left = 60 - (timezone.now() - recent_request.created_at).seconds
            return JsonResponse({
                'success': False,
                'message': f'Please wait {time_left} seconds before requesting another reset.'
            })
        
        # Generate reset token
        token = secrets.token_urlsafe(32)
        
        # Create password reset record
        PasswordReset.objects.create(user=user, token=token)
        
        # Generate reset URL
        reset_url = request.build_absolute_uri(f'/accounts/reset-password/{token}/')
        
        # Print to console for testing
        print(f"Password reset link for {user.email}: {reset_url}")
        
        # Send email
        email_sent = send_password_reset_email(user, reset_url)
        
        if email_sent:
            message = 'Password reset link sent! Check your email.'
        else:
            message = 'Password reset link generated but email failed to send. Check console.'
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        print(f"Error in request_password_reset: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


def reset_password_page(request, token):
    """Display password reset page"""
    try:
        reset_request = PasswordReset.objects.get(token=token)
        
        if not reset_request.is_valid():
            return render(request, 'accounts/password_reset_invalid.html', {
                'message': 'This password reset link has expired or been used.'
            })
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            if not new_password or len(new_password) < 8:
                return render(request, 'accounts/password_reset_form.html', {
                    'token': token,
                    'error': 'Password must be at least 8 characters long.'
                })
            
            if new_password != confirm_password:
                return render(request, 'accounts/password_reset_form.html', {
                    'token': token,
                    'error': 'Passwords do not match.'
                })
            
            # Reset password
            user = reset_request.user
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            reset_request.used = True
            reset_request.save()
            
            return render(request, 'accounts/password_reset_success.html')
        
        return render(request, 'accounts/password_reset_form.html', {'token': token})
        
    except PasswordReset.DoesNotExist:
        return render(request, 'accounts/password_reset_invalid.html', {
            'message': 'Invalid password reset link.'
        })
    except Exception as e:
        print(f"Error in reset_password_page: {e}")
        return render(request, 'accounts/password_reset_invalid.html', {
            'message': 'An error occurred. Please try again.'
        })