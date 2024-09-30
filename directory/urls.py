from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('directory/', views.directory_view, name='directory'),
    path('business/<int:pk>/', views.business_detail_view, name='business_detail'),  # Ensure this line is present
    path('membership/', views.become_member, name='become_member'),
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact_us, name='contact_us'),
]
