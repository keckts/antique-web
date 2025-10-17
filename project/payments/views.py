# payments/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

import stripe

from .models import Order, OrderItem
from antiques.models import Antique

stripe.api_key = settings.STRIPE_SECRET_KEY


# -------------------------
# 1. View all orders
# -------------------------
@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/orders/orders.html', {'orders': user_orders})


# -------------------------
# 2. Create order
# -------------------------
@login_required
def create_order(request, pk):  # pk = antique's UUID
    antique = get_object_or_404(Antique, id=pk)

    # ✅ You might want to check if antique is still available
    if antique.quantity < 1:
        return render(request, 'payments/orders/unavailable.html', {'antique': antique})

    # Create a new order and order item
    order = Order.objects.create(user=request.user)
    OrderItem.objects.create(order=order, antique=antique, quantity=1)  # Adjust quantity if needed

    # Redirect to checkout
    return redirect('payments:create_checkout_session', pk=order.id)


# -------------------------
# 3. Create Stripe Checkout Session
# -------------------------
@login_required
def create_checkout_session(request, pk):
    order = get_object_or_404(Order, id=pk, user=request.user)

    line_items = [
        {
            'price': item.antique.stripe_price_id,
            'quantity': item.quantity,
        }
        for item in order.orderitem_set.all()
    ]

    BASE_URL = "https://stunning-dollop-qw5g9q4v5rg2xxwj-8000.app.github.dev"  # ✅ Change in production

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=f"{BASE_URL}{reverse('dashboard')}?payment=success",
        cancel_url=f"{BASE_URL}{reverse('dashboard')}?payment=canceled",
    )

    order.stripe_session_id = session.id
    order.save()

    return redirect(session.url)


# -------------------------
# 4. Webhook to handle Stripe events
# -------------------------
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    # ✅ Handle successful checkout
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        try:
            order = Order.objects.get(stripe_session_id=session.id)
        except Order.DoesNotExist:
            return HttpResponse(status=404)

        order.status = 'paid'
        order.save()

        # ✅ Safely decrement stock
        for item in order.orderitem_set.all():
            antique = item.antique
            antique.quantity = max(0, antique.quantity - item.quantity)
            antique.save()

    return HttpResponse(status=200)


# -------------------------
# 5. Result page (optional)
# -------------------------
def checkout_result(request):
    success = request.GET.get('success') == 'true'
    canceled = request.GET.get('canceled') == 'true'

    context = {
        'success': success,
        'canceled': canceled,
    }
    return render(request, 'payments/checkout_result.html', context)
