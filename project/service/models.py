from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone

STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('published', 'Published'),
)

class BlogPost(models.Model):
    # Core Fields
    title = models.CharField(max_length=200)
    content = models.TextField() # HTML field
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # New Fields for Control and SEO
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft') # Draft/Published
    slug = models.SlugField(max_length=250, unique=True, blank=True) # URL-friendly title
    
    # Date/Time Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # Updates every time the post is saved

    topic = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)

    def __str__(self):
        return self.title
        
    # Optional: Automatically set slug when saving
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_reading_time(self):
        word_count = len(self.content.split())
        reading_time_minutes = max(1, word_count // 200) # Assuming average reading speed of 200 wpm
        return reading_time_minutes

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
    
class EmailTemplate(models.Model):
    """Model for storing email templates. Useful for drafts or to see past mass emails."""

    name = models.CharField(max_length=100, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField(blank=True, null=True)  # HTML content
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'
    
    