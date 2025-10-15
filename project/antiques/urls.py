from django.urls import path
from . import views

app_name = 'antiques'

urlpatterns = [
    path('view/', views.view_antiques, name='view_antiques'),
    path("antiques/<int:short_id>-<slug:slug>/", views.antique_detail, name="antique_detail"),
    path('antiques/new/', views.antique_form, name='create_antique'),
    path('antiques/<slug:slug>/', views.antique_form, name='edit_antique'),
    path('antiques/delete/<slug:slug>/', views.antique_delete, name='delete_antique'),

    path('add/', views.add_to_wishlist, name='add_to_wishlist'),  # New URL pattern for adding to wishlist
    path('wishlists/', views.wishlists, name='wishlists'),
    path('wishlists/<uuid:pk>/', views.wishlist_detail, name='wishlist_detail'),
    path('wishlists/delete/<uuid:pk>/', views.delete_wishlist, name='delete_wishlist'),
    path('wishlists/form/', views.wishlist_form, name='create_wishlist'),
    path('wishlists/form/<uuid:pk>/', views.wishlist_form, name='edit_wishlist'),
]