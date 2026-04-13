from django.shortcuts import render,redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Movie, Seat, Genre, Booking, Theater
from django.db.models import Sum, Count
from django.core.mail import send_mail
from django.conf import settings
import razorpay
from django.contrib.auth.models import User
from django.http import HttpResponse


# 0===============================
# AUTO RELEASE EXPIRED SEATS
# ===============================

def release_expired_seats():

    expired_time = timezone.now() - timedelta(minutes=5)

    expired_seats = Seat.objects.filter(
        status="reserved",
        reserved_at__lt=expired_time
    )

    for seat in expired_seats:
        seat.status = "available"
        seat.reserved_at = None
        seat.save()
# ===============================
# SEED DATA FUNCTION
# ===============================

def seed_data():
    if not Movie.objects.exists():

        g1 = Genre.objects.create(name="Animation", language="english")
        g2 = Genre.objects.create(name="Action", language="telugu")

        t1 = Theater.objects.create(name="Asian Sridevi")
        t2 = Theater.objects.create(name="PVR")

        m1 = Movie.objects.create(title="Tom & Jerry", genre=g1, language="english", price=100)
        m2 = Movie.objects.create(title="Raajasaab", genre=g2, language="telugu", price=150)

        for i in range(1, 5):
            Seat.objects.create(movie=m1, theater=t1, seat_number=f"A{i}")
            Seat.objects.create(movie=m2, theater=t2, seat_number=f"A{i}")
# ===============================
# MOVIE LIST + FILTERING
# ===============================

def movie_list(request):
    print("VIEW CALLED")  # debug

    # seed data once (optional)
    seed_data()


    movies = Movie.objects.all()
    genres = Genre.objects.all()

    genre_id = request.GET.get("genre")
    language = request.GET.get("language")

    if genre_id:
        movies = movies.filter(genre_id=genre_id)

    if language:
        movies = movies.filter(language=language)

    return render(request, "movies/movie_list.html", {
        "movies": movies,
        "genres": genres
    })

# ===============================
# MOVIE DETAIL
# ===============================

def movie_detail(request, movie_id):

    release_expired_seats()

    movie = get_object_or_404(Movie, id=movie_id)

    seats = Seat.objects.filter(movie=movie)

    return render(request, "movies/movie_detail.html", {
        "movie": movie,
        "seats": seats
    })


# ===============================
# RESERVE SEAT
# ===============================

def reserve_seat(request, seat_id):

    seat = get_object_or_404(Seat, id=seat_id)

    if seat.status == "available":

        seat.status = "reserved"
        seat.reserved_at = timezone.now()
        seat.save()

        return redirect("payment_page", seat_id=seat.id)

    return redirect("movie_list")


# ===============================
# CHECK TIMEOUT
# ===============================

def check_timeout(seat):

    if seat.status == "reserved" and seat.reserved_at:

        if timezone.now() - seat.reserved_at > timedelta(minutes=5):

            seat.status = "available"
            seat.reserved_at = None
            seat.save()


# ===============================
# PAYMENT PAGE (RAZORPAY)
# ===============================

def payment_page(request, seat_id):

    seat = get_object_or_404(Seat, id=seat_id)

    check_timeout(seat)

    if seat.status != "reserved":
        return redirect("movie_list")

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    # movie price dynamic
    amount = int(seat.movie.price * 100)

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    context = {
        "seat": seat,
        "order_id": order["id"],
        "amount": amount,
        "razorpay_key": settings.RAZORPAY_KEY_ID
    }

    return render(request, "movies/payment.html", context)


# ===============================
# CONFIRM BOOKING + EMAIL
# ===============================

def confirm_booking(request, seat_id):

    seat = get_object_or_404(Seat, id=seat_id)  # ✅ FIRST

    check_timeout(seat)

    user_email = request.GET.get("email")

    if seat.status == "reserved":

        # ✅ update seat
        seat.status = "booked"
        seat.save()

        # ✅ CREATE BOOKING (correct place)
        Booking.objects.create(
            movie=seat.movie,
            theater=seat.theater,
            number_of_tickets=1,
            total_price=seat.movie.price
        )

        subject = "Movie Ticket Confirmation 🎬"

        message = f"""
Booking Successful!

Movie: {seat.movie.title}
Seat Number: {seat.seat_number}
Ticket Price: ₹{seat.movie.price}

Enjoy your movie 🍿
"""

        if user_email:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [user_email],
                fail_silently=False
            )

        return render(request, "movies/success.html")

    return redirect("movie_list")

# ===============================
# PAYMENT FAILED
# ===============================

def payment_failed(request, seat_id):

    seat = get_object_or_404(Seat, id=seat_id)

    if seat.status == "reserved":

        seat.status = "available"
        seat.reserved_at = None
        seat.save()

    return render(request, "movies/payment_failed.html")


# ===============================
# ADMIN DASHBOARD ANALYTICS
# ===============================

def admin_dashboard(request):

    total_revenue = Booking.objects.aggregate(
        total=Sum("total_price")
    )["total"] or 0

    popular_movies = Movie.objects.annotate(
        bookings_count=Count("booking")
    ).order_by("-bookings_count")[:5]

    busiest_theaters = Theater.objects.annotate(
        bookings_count=Count("booking")
    ).order_by("-bookings_count")[:5]

    context = {
        "total_revenue": total_revenue,
        "popular_movies": popular_movies,
        "busiest_theaters": busiest_theaters
    }
    return render(request, "movies/analytics.html", context)
    
def success(request):
    return render(request, "movies/success.html")


# ===============================
# CREATE SUPERUSER (TEMP)
# ===============================

def create_admin(request):

    if not User.objects.filter(username="deepthi").exists():

        User.objects.create_superuser(
            username="deepthi",
            email="tu045044@gmail.com",
            password="Deepthi@123"
        )

        return HttpResponse("Superuser created")

    return HttpResponse("Already exists")