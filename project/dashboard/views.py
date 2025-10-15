from django.shortcuts import redirect, render
from antiques.models import Antique, DailyPick
from .models import Subscriber
from django.contrib import messages

def index(request): 
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    return render(request, 'dashboard/index.html')

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('index')

    # Get today's daily picks
    picks = DailyPick.get_today_picks()

    # Get the IDs of antiques already in today's picks
    pick_ids = picks.values_list('id', flat=True)

    # Get the 3 most recent antiques not in today's picks
    recent_antiques = (
        Antique.objects.exclude(id__in=pick_ids)
        .order_by('-created_at')[:3]
    )

    return render(
        request,
        'dashboard/main/dashboard.html',
        {
            'picks': picks,
            'recent_antiques': recent_antiques,
        },
    )

def subscribe(request): 
    """Handle email subscription form submission"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if email:
            # Check if email already exists
            if Subscriber.objects.filter(email=email).exists():
                messages.warning(request, 'This email is already subscribed!')
            else:
                # Create new subscriber
                Subscriber.objects.create(email=email)
                messages.success(request, 'Thank you for subscribing!')
        else:
            messages.error(request, 'Please provide a valid email address.')
    
    return redirect('index')