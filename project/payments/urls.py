from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('orders/', views.orders, name='orders'),
    path('create-order/<uuid:pk>/', views.create_order, name='create_order'),
    path('checkout/<uuid:pk>/', views.create_checkout_session, name='create_checkout_session'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('checkout-result/', views.checkout_result, name='checkout_result'),
    path('stripe/portal/', views.stripe_customer_portal, name='stripe_customer_portal'),
    path('invoice/<uuid:order_id>/', views.download_invoice, name='download_invoice'),
]
