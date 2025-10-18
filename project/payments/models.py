# payments/models.py
from django.db import models
from django.conf import settings
from antiques.models import Antique
import uuid

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('canceled', 'Canceled'),
        ('fulfilled', 'Fulfilled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    antiques = models.ManyToManyField(Antique, through='OrderItem')
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    stripe_invoice_pdf = models.URLField(blank=True, null=True)  # PDF download link

    def __str__(self):
        return f"Order {self.id} by {self.user}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.orderitem_set.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    antique = models.ForeignKey(Antique, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.antique.price * self.quantity
