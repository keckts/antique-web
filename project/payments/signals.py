# payments/signals.py

import stripe
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from antiques.models import Antique

stripe.api_key = settings.STRIPE_SECRET_KEY

@receiver(post_save, sender=Antique)
def create_stripe_product(sender, instance, created, **kwargs):
    # Only create Stripe product if:
    # 1. The Antique is newly created
    # 2. It has a price > 0
    # 3. It is not sold (optional, if you only create for sale items)

    if created and instance.price > 0 and not instance.is_sold:
        # Avoid creating multiple Stripe products if already exists
        if not hasattr(instance, 'stripe_product_id') or not instance.stripe_product_id:
            product = stripe.Product.create(
                name=f"{instance.title}",
                description=instance.description or "Antique for sale",
            )
            
            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(instance.price * 100),  # Stripe uses cents
                currency="aud",
            )
            
            # Save the Stripe product ID on the instance
            instance.stripe_product_id = product.id
            instance.stripe_price_id = price.id
            instance.save(update_fields=['stripe_product_id', 'stripe_price_id'])
