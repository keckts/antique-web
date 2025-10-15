from django.db import models
from django.conf import settings
import uuid 
import random
from django.utils.text import slugify
from django.utils import timezone

class BaseModel(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Good note: always include default=uuid.uuid4 for UUIDField to auto-generate unique IDs
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        abstract = True

class Antique(BaseModel):
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_sold = models.BooleanField(default=False)
    type_of_antique = models.CharField(max_length=100)

    slug = models.SlugField(max_length=255, unique=True, blank=True)
    short_id = models.PositiveIntegerField(unique=True, editable=False, null=True, blank=True)
    
    dimensions = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    additional_info = models.TextField(blank=True)

    seller = models.ForeignKey('accounts.Seller', on_delete=models.SET_NULL, null=True, blank=True, related_name='antiques')

    def __str__(self):
        return f"{self.title} ({self.id})"

    def get_absolute_url(self):
        return f"/antiques/{self.short_id}-{self.slug}/"

    def save(self, *args, **kwargs):
        # Generate short_id only once
        if not self.short_id:
            while True:
                candidate = random.randint(10000, 99999)
                if not Antique.objects.filter(short_id=candidate).exists():
                    self.short_id = candidate
                    break

        # Handle slug: use user-provided slug if present; otherwise generate from title
        if not self.slug:  # slug field blank => auto-generate
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while Antique.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = unique_slug
        # else: user entered a slug, keep it as-is

        super().save(*args, **kwargs)

class AntiqueImage(models.Model):
    antique = models.ForeignKey(Antique, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='antiques/')
    
    def __str__(self):
        return f"Image for {self.antique.title} ({self.id})"
        
class Wishlist(BaseModel):
    antiques = models.ManyToManyField(Antique, related_name='wishlists', blank=True)

    def __str__(self):
        return f"{self.title}"

class DailyPick(models.Model):
    date = models.DateField(unique=True)
    picks = models.ManyToManyField('Antique', related_name='daily_picks')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Picks for {self.date}"
    
    @staticmethod
    def get_today_picks():
        today = timezone.localdate()
        daily_pick, created = DailyPick.objects.get_or_create(date=today)
        if daily_pick.picks.count() == 0:
            # auto-fill 3 random antiques if none were chosen
            antiques = list(Antique.objects.all())
            if antiques:
                daily_pick.picks.set(random.sample(antiques, min(3, len(antiques))))
        return daily_pick.picks.all()