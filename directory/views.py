from django.shortcuts import get_object_or_404, render
from .models import Business, BlogPost,Category


def home(request):
    return render(request, 'directory/home.html')

def directory_view(request):
    # Get all categories for the dropdown
    categories = Category.objects.all()

    # Get the search query from the request (if any)
    search_query = request.GET.get('q', '')

    # Get the selected category from the dropdown or from the URL query parameters (if any)
    selected_category_id = request.GET.get('category', None)

    # Filter businesses based on the search query and selected category
    businesses = Business.objects.all()

    if search_query:
        businesses = businesses.filter(name__icontains=search_query)

    if selected_category_id:
        businesses = businesses.filter(category__id=selected_category_id)

    context = {
        'businesses': businesses,
        'categories': categories,
        'search_query': search_query,
        'selected_category_id': selected_category_id,
    }

    return render(request, 'directory/directory.html', context)






def business_detail_view(request, pk):
    business = get_object_or_404(Business, pk=pk)
    return render(request, 'directory/business_detail.html', {'business': business})


def become_member(request):
    return render(request, 'directory/become_a_member.html')

def blog(request):
    # First filter for promotions and then append the non-promotion posts
    blog_posts = list(BlogPost.objects.filter(isOnPromotion=True)) + list(BlogPost.objects.filter(isOnPromotion=False))
    return render(request, 'directory/blog.html', {'blog_posts': blog_posts})

def blog_detail(request, pk):
    # Retrieve the blog post by its primary key (pk)
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'directory/blog_detail.html', {'post': post})

def contact_us(request):
    return render(request, 'directory/contact_us.html')
