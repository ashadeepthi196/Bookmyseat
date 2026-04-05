"""
URL configuration for bookmyseat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from movies.views import movie_list,admin_dashboard
from movies.admin import custom_admin_site 

urlpatterns = [
    path('admin/', custom_admin_site.urls), 

    path('', movie_list, name='home'),

    path('admin-dashboard/',admin_dashboard,name='admin-dashboard'),

    path('movies/', include('movies.urls')),
]