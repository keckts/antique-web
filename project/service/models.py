from django.db import models
from django.conf import settings
from django.utils.text import slugify

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