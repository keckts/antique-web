from django.shortcuts import render, redirect, get_object_or_404
from .models import BlogPost, Subscriber
from .forms import BlogPostForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .utils import only_superuser

def blogs(request):
    posts = BlogPost.objects.all()
    return render(request, 'service/blog/blogs.html', {'posts': posts})

def blog_detail(request, slug): 
    post = BlogPost.objects.get(slug=slug)
    username = post.owner.email.split('@')[0] if post.owner and post.owner.email else 'Unknown'
    return render(request, 'service/blog/blog_detail.html', {'post': post, 'username': username})

def blog_form(request, pk=None):
    antique = None
    
    if pk:
        antique = get_object_or_404(BlogPost, pk=pk, owner=request.user)
        
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=antique)
        
        if form.is_valid():
            new_post = form.save(commit=False)
            
            if not pk:
                new_post.owner = request.user
            new_post.save()
            return redirect('service:blogs')
    else:
        form = BlogPostForm(instance=antique)

    return render(request, 'service/blog/blog_form.html', {'form': form})

def about_us(request):
    return render(request, 'service/general/about_us.html')

def terms_and_conditions(request):
    return render(request, 'service/general/terms_and_conditions.html')

def privacy_policy(request):
    return render(request, 'service/general/privacy_policy.html')



from django.contrib import messages

def subscribe(request, in_settings='false'):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if email:
            if Subscriber.objects.filter(email=email).exists():
                messages.add_message(
                    request,
                    messages.WARNING,
                    'This email is already subscribed!',
                    extra_tags='subscriber'
                )
            else:
                Subscriber.objects.create(email=email)
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Thank you for subscribing!',
                    extra_tags='subscriber'
                )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                'Please provide a valid email address.',
                extra_tags='subscriber'
            )

    if in_settings == 'true': # django only has strings no booleans :(
        return redirect('accounts:settings')
    
    return redirect('index')


def unsubscribe(request):
    if request.method == 'POST':
        email = request.user.email  # Get email from logged-in user
        
        if email:
            try:
                subscriber = Subscriber.objects.get(email=email)
                subscriber.delete()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'You have been unsubscribed successfully.',
                    extra_tags='subscriber'
                )
            except Subscriber.DoesNotExist:
                messages.add_message(
                    request,
                    messages.ERROR,
                    'This email is not subscribed.',
                    extra_tags='subscriber'
                )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                'Please provide a valid email address.',
                extra_tags='subscriber'
            )

    return redirect('accounts:settings')
  
def send_mass_email(subject, message, recipient_list):
    """
    Send emails to a list of recipients.
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )

from django.http import JsonResponse
from .models import EmailTemplate
from django.views.decorators.csrf import csrf_exempt
import json

def send_mass_email_page(request):
    drafts= EmailTemplate.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'service/admin/mass_email.html', {'drafts': drafts})

def send_mass_email_view(request):
    if request.method == "POST":
        subject = request.POST['subject']
        body = request.POST['message']
        image = request.FILES.get('image')
        # Your send_mass_email function
        recipient_list = [s.email for s in Subscriber.objects.filter(is_active=True)]
        send_mass_email(subject, body, recipient_list)
        messages.success(request, "Emails sent successfully!")
    return redirect('service:send_mass_email_page')

@csrf_exempt
def save_email_draft(request):
    if request.method == "POST":
        data = json.loads(request.body)
        EmailTemplate.objects.create(
            name=data.get('subject')[:50],  # simple name
            subject=data.get('subject'),
            body=data.get('body'),
            created_by=request.user
        )
        return JsonResponse({"status": "ok"})

@only_superuser
def admin_panel(request):
    return render(request, 'service/admin/admin_panel.html')

