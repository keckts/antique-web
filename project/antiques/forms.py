# No changes needed for imports
from django import forms
from .models import Antique, Wishlist, AntiqueImage
from django.forms import modelformset_factory
from project.generic_functions import random_text



class AntiqueForm(forms.ModelForm):
    class Meta:
        model = Antique
        exclude = ['id', 'owner', 'short_id', 'created_at', 'updated_at', 'is_sold', 'seller']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Rare Victorian Teapot'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 1, 'placeholder': 'Brief description (Shows in listings)'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detailed content about the antique'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.05'}),
            'type_of_antique': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generated from title if left blank'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Height 32cm x Width 20cm x Depth 15cm'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '1'}),
            'additional_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 1, 'placeholder': 'Any additional information'}),
        }


class AntiqueImageForm(forms.ModelForm):
    class Meta:
        model = AntiqueImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }



# Formset for multiple images
AntiqueImageFormSet = modelformset_factory(
    AntiqueImage,
    form=AntiqueImageForm,
    extra=1,  # number of blank image fields to display
    can_delete=True
)



# --- FIX APPLIED HERE ---
class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        # 1. FIX: EXCLUDE the 'user' field, which is required but set by the view.
        # 2. Add 'id' just in case, though it's typically auto-excluded.
        exclude = ['user', 'id']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., European Porcelain' # Added a placeholder for clarity
            }),
        }