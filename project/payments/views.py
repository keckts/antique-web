from django.shortcuts import render

def orders(request):
    return render(request, 'payments/orders/orders.html')