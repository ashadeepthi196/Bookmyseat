from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum, Count
from .models import Movie, Genre, Seat, Theater, Booking

# Custom Admin Dashboard
class CustomAdminSite(admin.AdminSite):
    site_header = "BookMySeat Admin Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_view(self.analytics_view)),
        ]
        return custom_urls + urls

    def analytics_view(self, request):
        total_revenue = Booking.objects.aggregate(
            Sum('total_price')
        )['total_price__sum'] or 0

        popular_movies = (
            Booking.objects
            .values('movie__title')
            .annotate(total=Count('id'))
            .order_by('-total')[:5]
        )

        busiest_theaters = (
            Booking.objects
            .values('theater__name')
            .annotate(total=Count('id'))
            .order_by('-total')[:5]
        )

        context = {
            "total_revenue": total_revenue,
            "popular_movies": popular_movies,
            "busiest_theaters": busiest_theaters,
        }

        return render(request, "admin/analytics.html", context)


# Replace default admin
custom_admin_site = CustomAdminSite(name="custom_admin")


# Register normal models
custom_admin_site.register(Movie)
custom_admin_site.register(Genre)
custom_admin_site.register(Seat)
custom_admin_site.register(Theater)
custom_admin_site.register(Booking)
