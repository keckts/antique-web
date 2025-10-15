from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Antique, Wishlist, AntiqueImage, DailyPick
from .forms import AntiqueForm, WishlistForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from project.generic_functions import _generic_form_view, _generic_delete, random_text

def get_wishlists(user):
    if user.is_authenticated:
        return Wishlist.objects.filter(owner=user).order_by('-created_at')[:5]
    return []

def view_antiques(request):
    antiques = Antique.objects.filter(is_sold=False).order_by('-created_at')
    # Get unique antique types for the filter dropdown
    antique_types = Antique.objects.filter(is_sold=False).values_list('type_of_antique', flat=True).distinct().order_by('type_of_antique')
    
    return render(request, 'antiques/view/view_antiques.html', {
        'antiques': antiques,
        'wishlists': get_wishlists(request.user),
        'antique_types': antique_types
    })
    
def antique_detail(request, short_id, slug):
    antique = get_object_or_404(Antique, short_id=short_id, slug=slug)
    return render(request, 'antiques/view/antique_detail.html', {'antique': antique, 'wishlists': get_wishlists(request.user)})

@login_required
@require_POST
def antique_delete(request, slug):
    antique = get_object_or_404(Antique, slug=slug, owner=request.user)
    title = antique.title  # store before deleting
    antique.delete()
    messages.success(request, f'"{title}" was successfully deleted.')
    return redirect('antiques:view_antiques') 

@login_required
def antique_form(request, slug=None):
    """
    Create or edit an Antique item with multiple image uploads (no formset).
    Uses <input type='file' name='images' multiple> in the template.
    """
    antique = None
    editing = bool(slug)

    if editing:
        antique = get_object_or_404(Antique, slug=slug, owner=request.user)
        title = f"Edit Antique: {antique.title}"
    else:
        title = "Create Antique"

    if request.method == "POST":
        form = AntiqueForm(request.POST, request.FILES, instance=antique)

        print("\n--- DEBUG: POST Request ---")
        print("Files received:", request.FILES)
        print("Images received:", request.FILES.getlist("images"))
        print("---------------------------\n")

        if form.is_valid():
            obj = form.save(commit=False)
            if not editing:
                obj.owner = request.user
                obj.seller = request.user.seller  # Automatically assign seller based on logged-in user
            obj.save()
            form.save_m2m()

            # Save uploaded images manually
            images = request.FILES.getlist("images")
            if images:
                for image_file in images:
                    AntiqueImage.objects.create(antique=obj, image=image_file)
                    print(f"DEBUG: Saved image -> {image_file.name}")
            else:
                print("DEBUG: No images uploaded.")

            messages.success(request, f"'{obj.title}' saved successfully!")
            print("DEBUG: Antique saved successfully.\n")
            return redirect("antiques:antique_detail", short_id=obj.short_id, slug=obj.slug)

        else:
            print("DEBUG: Form is not valid.")
            print("Form errors:", form.errors)
            messages.error(request, "Please correct the errors below.")

    else:
        print("\n--- DEBUG: GET Request ---")
        if editing:
            print(f"Editing existing antique: {antique.title}")
        else:
            print("Creating new antique.")
        print("---------------------------\n")

        form = AntiqueForm(instance=antique)
        
    initial_data = {'title': random_text(), 'description': 'A beautiful antique item', 'content': 'Detailed content about the antique', 'price': '100.00', 'type_of_antique': 'General'}

    form = AntiqueForm(initial=initial_data)

    return render(request, "antiques/create/antique_form.html", {
        "form": form,
        "antique": antique,
        "title": title,
        "editing": editing,
    })

@login_required
def add_to_wishlist(request):
    print("DEBUG: add_to_wishlist called")
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        antique_id = request.POST.get("antique_id")
        wishlist_id = request.POST.get("wishlist_id")

        antique = get_object_or_404(Antique, id=antique_id)
        wishlist = get_object_or_404(Wishlist, id=wishlist_id, owner=request.user)

        wishlist.antiques.add(antique)
        print(f"DEBUG: Added '{antique.title}' to wishlist '{wishlist.title}'")
        return JsonResponse({"success": True})
    print("DEBUG: Invalid request to add to wishlist")
    return JsonResponse({"success": False}, status=400)
    
def wishlists(request):
    wishlists = Wishlist.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'antiques/wishlists/wishlists.html', {'wishlists': wishlists})

def wishlist_detail(request, pk):
    wishlist = get_object_or_404(Wishlist, pk=pk, owner=request.user)
    print(wishlist.antiques.all())
    return render(request, 'antiques/wishlists/wishlist_detail.html', {'wishlist': wishlist})

def delete_wishlist(request, pk):
    return _generic_delete(request, Wishlist, pk, 'antiques:wishlists')


@login_required
def wishlist_form(request, pk=None):
    """
    Create or edit a Wishlist. Automatically assigns `owner` on creation.
    """
    instance = None
    if pk:
        instance = get_object_or_404(Wishlist, pk=pk, owner=request.user)

    if request.method == "POST":
        form = WishlistForm(request.POST, instance=instance)
        if form.is_valid():
            wishlist = form.save(commit=False)
            if not pk:  # Only set owner on creation
                wishlist.owner = request.user
            wishlist.save()
            form.save_m2m()
            
            messages.success(request, f"'{wishlist.title}' saved successfully!")
            return redirect('antiques:wishlist_detail', pk=wishlist.pk)  # redirect to wishlist detail view
        else:
            messages.error(request, "Please correct the errors below.")
            print("Form errors:", form.errors)
    else:
        form = WishlistForm(instance=instance)

    return render(request, "antiques/wishlists/wishlist_form.html", {"form": form})
