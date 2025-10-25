from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login_view/', views.login_view, name='login_view'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('signup_view/', views.signup_view, name='signup_view'),

    path('settings/', views.settings_view, name='settings'),
    path('seller-form/', views.seller_form, name='seller_form'),  # New URL for seller form
    
    path('send-verification-code/', views.send_verification_code_ajax, name='send_verification_code_ajax'),
    path('verify-email/', views.verify_email_ajax, name='verify_email_ajax'),
    path('verify-password/', views.verify_password, name='verify_password'),
    
    # Password Reset URLs
    path('request-password-reset/', views.request_password_reset, name='request_password_reset'),
    path('reset-password/<str:token>/', views.reset_password_page, name='reset_password_page'),

]
