from django import forms
# Assuming your model is in an app called 'blog' or similar, 
# you'll need to adjust the import path if necessary.
from .models import BlogPost 

class BlogPostForm(forms.ModelForm):
    """
    A ModelForm for creating and editing BlogPost objects.
    Excludes fields set automatically (owner, dates, slug).
    """

    class Meta:
        model = BlogPost
        # Fields the user needs to fill out on the form
        fields = ['title', 'content', 'topic', 'image', 'status']
        
        # Apply Bootstrap classes (assuming you are using Bootstrap 5)
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'The title of your post (e.g., Why Waverley Antique Bazaar is Heaven)'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Write your full blog content here (supports HTML formatting).'
            }),
            'topic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Restoration, History, Collecting'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select', # Use form-select for select inputs in Bootstrap
            })
        }

        help_texts = {
            'image': 'Upload a clear, main photo for your blog post.',
            'status': 'Set to "Published" to make the post visible to everyone.',
        }
