# payments/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

import stripe

from .models import Order, OrderItem
from antiques.models import Antique

stripe.api_key = settings.STRIPE_SECRET_KEY


# -------------------------
# 1. View all orders
# -------------------------
@login_required
def orders(request):
    order_objects = Order.objects.filter(user=request.user).order_by('-created_at')
    stripe_orders = []

    for order in order_objects:
        stripe_info = {}
        if order.stripe_session_id:
            try:
                session = stripe.checkout.Session.retrieve(order.stripe_session_id)
                stripe_info = {
                    "status": session.payment_status,
                    "amount_total": session.amount_total / 100 if session.amount_total else 0,
                    "currency": session.currency.upper() if session.currency else 'USD',
                    "receipt_url": None
                }
                
                # Get payment intent for receipt URL
                if session.payment_intent:
                    try:
                        payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
                        stripe_info.update({
                            "status": payment_intent.status,
                            "amount_received": payment_intent.amount_received / 100,
                        })
                        
                        # Get receipt URL from the latest charge
                        if payment_intent.latest_charge:
                            charge = stripe.Charge.retrieve(payment_intent.latest_charge)
                            stripe_info["receipt_url"] = charge.receipt_url
                            
                    except stripe.StripeError:
                        pass
                        
            except stripe.StripeError as e:
                stripe_info = {"error": str(e)}

        stripe_orders.append({
            "order": order,
            "stripe": stripe_info,
        })

    return render(request, "payments/orders/orders.html", {"stripe_orders": stripe_orders})

# -------------------------
# 2. Create Checkout Session (Direct)
# -------------------------
@login_required
def create_order(request, pk):  # pk = antique's UUID
    antique = get_object_or_404(Antique, id=pk)

    # ✅ Check if antique is still available
    if antique.quantity < 1:
        return render(request, 'payments/orders/unavailable.html', {'antique': antique})

    # Don't create order yet - only create it when payment succeeds
    # Redirect directly to checkout session creation
    return redirect('payments:create_checkout_session', pk=pk)


# -------------------------
# 3. Create Stripe Checkout Session
# -------------------------
@login_required
def create_checkout_session(request, pk):
    antique = get_object_or_404(Antique, id=pk)

    # Ensure user has a Stripe customer ID
    if not request.user.stripe_customer_id:
        try:
            customer = stripe.Customer.create(
                email=request.user.email,
                name=request.user.get_full_name() or request.user.email,
            )
            request.user.stripe_customer_id = customer.id
            request.user.save()
            print(f"✅ Created Stripe customer for {request.user.email}: {customer.id}")
        except stripe.StripeError as e:
            print(f"❌ Failed to create Stripe customer: {e}")

    line_items = [{
        'price': antique.stripe_price_id,
        'quantity': 1,
    }]

    # Dynamically get base URL (ngrok or local)
    scheme = 'https' if request.is_secure() else 'http'
    host = request.get_host()  # ngrok URL when running via ngrok
    BASE_URL = f"{scheme}://{host}"

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        customer=request.user.stripe_customer_id,  # Link to customer
        success_url=f"{BASE_URL}{reverse('payments:checkout_result')}?success=true",
        cancel_url=f"{BASE_URL}{reverse('payments:checkout_result')}?canceled=true",
        metadata={
            'user_id': request.user.id,
            'antique_id': str(antique.id),
            'quantity': '1',
        }
    )

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
        print("⚠️ Webhook signature verification failed")
        return HttpResponse(status=400)

    print(f"🔔 Received webhook event: {event['type']}")

    # -----------------------------
    # 1️⃣ Handle successful checkout - CREATE ORDER HERE
    # -----------------------------
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(f"💳 Processing checkout session: {session['id']}")

        # Extract metadata from session
        metadata = session.get('metadata', {})
        user_id = metadata.get('user_id')
        antique_id = metadata.get('antique_id')
        quantity = int(metadata.get('quantity', 1))

        if not user_id or not antique_id:
            print("❌ Missing user_id or antique_id in session metadata")
            return HttpResponse(status=400)

        try:
            # Get user and antique
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            antique = Antique.objects.get(id=antique_id)
            
            print(f"📦 Creating order for {user.email} - {antique.title}")

            # Create order and order item ONLY when payment succeeds
            order = Order.objects.create(
                user=user,
                stripe_session_id=session['id'],
                status='paid'
            )
            OrderItem.objects.create(
                order=order,
                antique=antique,
                quantity=quantity
            )
            print(f"✅ Order {order.id} created and marked as paid")

            # ✅ Safely decrement stock
            antique.quantity = max(0, antique.quantity - quantity)
            antique.save()
            print(f"📦 Updated stock for {antique.title}: {antique.quantity}")

        except (User.DoesNotExist, Antique.DoesNotExist) as e:
            print(f"❌ Error finding user or antique: {e}")
            return HttpResponse(status=404)
        except Exception as e:
            print(f"❌ Error creating order: {e}")
            return HttpResponse(status=500)

    # -----------------------------
    # 2️⃣ Handle invoice finalization / PDF
    # -----------------------------
    elif event['type'] in ['invoice.finalized', 'invoice.payment_succeeded']:
        invoice = event['data']['object']
        print(f"📄 Invoice event: {invoice['id']}")

        # Try to find order using payment intent
        order = None
        payment_intent_id = invoice.get('payment_intent')
        if payment_intent_id:
            try:
                orders = Order.objects.filter(stripe_session_id__isnull=False)
                for ord in orders:
                    try:
                        session = stripe.checkout.Session.retrieve(ord.stripe_session_id)
                        if session.payment_intent == payment_intent_id:
                            order = ord
                            break
                    except stripe.error.StripeError:
                        continue
            except stripe.error.StripeError as e:
                print(f"❌ Stripe error fetching payment intent: {e}")

        if order and invoice.get('invoice_pdf'):
            order.stripe_invoice_pdf = invoice['invoice_pdf']
            order.save()
            print(f"✅ Invoice PDF saved for order {order.id}")
        elif not order:
            print("❌ Could not find associated order for invoice")

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

# -------------------------
# 6. stripe Customer Portal
#-------------------------


@login_required
def stripe_customer_portal(request):
    # Create Stripe customer if they don't have one
    if not request.user.stripe_customer_id:
        try:
            customer = stripe.Customer.create(
                email=request.user.email,
                name=request.user.get_full_name() or request.user.email,
            )
            request.user.stripe_customer_id = customer.id
            request.user.save()
            print(f"✅ Created Stripe customer for portal access: {customer.id}")
        except stripe.StripeError as e:
            print(f"❌ Failed to create Stripe customer: {e}")
            messages.error(request, "Unable to access customer portal at this time.")
            return redirect('dashboard:dashboard')

    # Create a session for the Stripe Customer Portal
    try:
        session = stripe.billing_portal.Session.create(
            customer=request.user.stripe_customer_id,
            return_url=request.build_absolute_uri('/dashboard/')  # where user returns after portal
        )
        # Redirect user to the portal
        return redirect(session.url)
    except stripe.StripeError as e:
        print(f"❌ Failed to create customer portal session: {e}")
        messages.error(request, "Unable to access customer portal at this time.")
        return redirect('dashboard:dashboard')


# -------------------------
# 7. Download Invoice PDF
# -------------------------
@login_required
def download_invoice(request, order_id):
    """Handle invoice download for a specific order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.stripe_invoice_pdf:
        return redirect(order.stripe_invoice_pdf)
    else:
        # Try to get the invoice from Stripe directly
        if order.stripe_session_id:
            try:
                session = stripe.checkout.Session.retrieve(order.stripe_session_id)
                if session.payment_intent:
                    payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
                    
                    # List invoices for this payment intent
                    invoices = stripe.Invoice.list(payment_intent=payment_intent.id)
                    if invoices.data:
                        invoice = invoices.data[0]  # Get the first (most recent) invoice
                        if invoice.invoice_pdf:
                            # Save the PDF URL for future use
                            order.stripe_invoice_pdf = invoice.invoice_pdf
                            order.save()
                            return redirect(invoice.invoice_pdf)
            except stripe.StripeError:
                pass
        
        # If no invoice found, return error
        return JsonResponse({'error': 'Invoice not available yet'}, status=404)

