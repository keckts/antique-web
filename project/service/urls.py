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
]
