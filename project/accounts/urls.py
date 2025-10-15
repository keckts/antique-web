from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login_view/', views.login_view, name='login_view'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('signup_view/', views.signup_view, name='signup_view'),

    path('settings/', views.settings, name='settings'),
    path('seller-form/', views.seller_form, name='seller_form'),  # New URL for seller form
    
    path('verify-password/', views.verify_password, name='verify_password'),  # New URL for password verification
]