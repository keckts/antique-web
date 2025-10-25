from django.urls import path
from . import views

app_name = 'service'

urlpatterns = [
    path('blogs/', views.blogs, name='blogs'),
    path('blogs/new/', views.blog_form, name='create_blog'),
    path('blogs/edit/<slug:slug>/', views.blog_form, name='edit_blog'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),

    path('about-us/', views.about_us, name='about_us'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),

    path('subscribe/<str:in_settings>/', views.subscribe, name='subscribe'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),

    path('send-mass-email/', views.send_mass_email_view, name='send_mass_email_view'),
    path('save-email-draft/', views.save_email_draft, name='save_email_draft'),
    path('send-mass-email-page/', views.send_mass_email_page, name='send_mass_email_page'),

    path('admin-panel/', views.admin_panel, name='admin_panel'),



]
