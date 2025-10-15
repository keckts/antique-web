from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random

@login_required
def _generic_form_view(request, form_class, template_name, success_url_name, pk=None, extra_context=None):
    """
    Generic form view to handle creation or editing of model instances.
    
    - pk: If provided, edits the existing object; otherwise, creates a new one.
    - success_url_name: Can be a URL name string for list views, or a callable returning a URL (e.g., detail view).
    """
    model_class = form_class._meta.model
    instance = None

    if pk is not None:
        instance = get_object_or_404(model_class, pk=pk, owner=request.user)

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)

            # Automatically set owner or user if applicable
            if hasattr(obj, "owner") and not getattr(obj, "owner", None):
                obj.owner = request.user
            elif hasattr(obj, "user") and not getattr(obj, "user", None):
                obj.user = request.user

            obj.save()
            form.save_m2m()

            messages.success(request, f"'{obj}' saved successfully!")

            # Smart redirect:
            # If the model has a slug, use it; else use pk; else just redirect to the list
            if hasattr(obj, "slug") and obj.slug:
                if callable(success_url_name):
                    return redirect(success_url_name(obj))
                else:
                    return redirect(success_url_name, slug=obj.slug)
            elif hasattr(obj, "pk") and obj.pk:
                if callable(success_url_name):
                    return redirect(success_url_name(obj))
                else:
                    return redirect(success_url_name, pk=obj.pk)
            else:
                return redirect(success_url_name)
        else:
            messages.error(request, "Please correct the errors below.")
            print("Form errors:", form.errors)
    else:
        form = form_class(instance=instance)

    context = {"form": form}
    if extra_context:
        context.update(extra_context)

    return render(request, template_name, context)

@login_required
def _generic_form_view(request, form_class, template_name, success_url_name, instance=None, extra_context=None):
    
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=instance)
        
        if form.is_valid():
            obj = form.save(commit=False)
            
            # Set owner for Antique or user for Wishlist if creating a new object
            if instance is None:
                obj.owner = request.user if hasattr(obj, 'owner') else None
                print(f"Set owner to {obj.owner}")
            
            obj.save()
            form.save_m2m()

            messages.success(request, f"'{obj.title}' saved successfully!")

            # Redirect using slug if available, else pk
            if hasattr(obj, 'slug') and obj.slug:
                return redirect(success_url_name, slug=obj.slug)

            return redirect(success_url_name)
        else:
            messages.error(request, "Please correct the errors below.")
            print(f"Form errors: {form.errors}")
    else:
        form = form_class(instance=instance)

    context = {"form": form}
    if extra_context:
        context.update(extra_context)

    return render(request, template_name, context)


def _generic_delete(request, model_class, pk_or_slug, success_url_name):
    """
    Generic utility function to delete a model instance by either its PK or slug.
    Ensures the user owns the object before deletion.
    """
    instance = None

    # Try to get by primary key first
    try:
        instance = model_class.objects.get(pk=pk_or_slug, owner=request.user)
        print(f"DEBUG: Found instance by PK ({pk_or_slug})")
    except (model_class.DoesNotExist, ValueError):
        print(f"DEBUG: No instance found by PK ({pk_or_slug}). Trying slug...")
        instance = model_class.objects.filter(slug=pk_or_slug, owner=request.user).first()

    # If not found by PK, try slug
    if instance is None:
        instance = get_object_or_404(model_class, slug=pk_or_slug, owner=request.user)
        print(f"DEBUG: Found instance by slug ({pk_or_slug})")

    instance.delete()

    return redirect(success_url_name)

def random_text():
    word = ["blue", "red", "green", "yellow", "purple", "orange", "black", "white", "silver", "gold"]
    number = random.randint(1,100)
    return f"{random.choice(word)}-{number}"