from django.shortcuts import redirect, render
from antiques.models import Antique, DailyPick
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
        Antique.objects.exclude(id__in=pick_ids).exclude(quantity=0)
        .order_by('-created_at')[:3]
    )

    recent_sold_antiques = (
        Antique.objects.filter(quantity=0)
        .order_by('-created_at')[:3]
    )

    print(recent_sold_antiques)


    return render(
        request,
        'dashboard/main/dashboard.html',
        {
            'picks': picks,
            'recent_antiques': recent_antiques,
            'recent_sold_antiques': recent_sold_antiques,
        },
    )

