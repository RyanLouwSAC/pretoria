from django.contrib import admin
from .models import Business, Category, BlogPost, Membership

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'contact_number', 'email')
    search_fields = ('name', 'category__name')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at')
    search_fields = ('title',)

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('business', 'contact_info')
