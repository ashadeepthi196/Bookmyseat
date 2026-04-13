from django.urls import path, include
from django.contrib import admin
from movies import views   # ✅ ADD THIS
from movies.admin import custom_admin_site

urlpatterns = [
    
    # Custom Admin
    path('admin/', custom_admin_site.urls),

    # Home page
    path('', views.movie_list, name='home'),

    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),

    # App URLs
    path('movies/', include('movies.urls')),

    # Create superuser
    path('create-admin/', views.create_admin),
]