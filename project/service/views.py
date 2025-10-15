from django.shortcuts import render, redirect, get_object_or_404
from .models import BlogPost
from .forms import BlogPostForm

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
    return render(request, 'service/about_us.html')

def terms_and_conditions(request):
    return render(request, 'service/terms_and_conditions.html')

def privacy_policy(request):
    return render(request, 'service/privacy_policy.html')