from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('directory/', views.directory_view, name='directory'),
    path('business/<int:pk>/', views.business_detail_view, name='business_detail'),
    path('membership/', views.become_member, name='become_member'),
    path('blog/', views.blog, name='blog'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('contact/', views.contact_us, name='contact_us'),
]
