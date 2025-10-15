from django.db import models
from django.utils import timezone

class Subscriber(models.Model):
    """Model for storing email subscribers"""
    email = models.EmailField(unique=True, max_length=255)
    subscribed_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'
    
    def __str__(self):
        return self.email