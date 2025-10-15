from django.urls import path, include
from . import views

app_name = 'payments'

urlpatterns = [
    path('orders/', views.orders, name='orders'),
]