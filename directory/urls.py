from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('directory/', views.directory_view, name='directory'),
    path('membership/', views.become_member, name='become_member'),
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact_us, name='contact_us'),
]
