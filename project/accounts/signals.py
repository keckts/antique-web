from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import stripe
from .models import CustomUser

stripe.api_key = settings.STRIPE_SECRET_KEY

@receiver(post_save, sender=CustomUser)
def create_stripe_customer(sender, instance, created, **kwargs):
    if created and not instance.stripe_customer_id:
        customer = stripe.Customer.create(
            email=instance.email,
            name=instance.get_full_name() or instance.email,
        )
        instance.stripe_customer_id = customer.id
        instance.save()
