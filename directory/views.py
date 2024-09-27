from django.shortcuts import render
from .models import Business, BlogPost

def home(request):
    return render(request, 'directory/home.html')

def directory_view(request):
    businesses = Business.objects.all()
    return render(request, 'directory/directory.html', {'businesses': businesses})

def become_member(request):
    return render(request, 'directory/become_a_member.html')

def blog(request):
    blog_posts = BlogPost.objects.all()
    return render(request, 'directory/blog.html', {'blog_posts': blog_posts})

def contact_us(request):
    return render(request, 'directory/contact_us.html')
