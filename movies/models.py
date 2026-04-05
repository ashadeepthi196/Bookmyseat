from django.db import models
from django.utils import timezone


# =========================
# GENRE MODEL
# =========================

class Genre(models.Model):

    LANGUAGE_CHOICES = [
        ('telugu', 'TELUGU'),
        ('hindi', 'HINDI'),
        ('english', 'ENGLISH'),
    ]

    name = models.CharField(max_length=100)

    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default='telugu'
    )

    def __str__(self):
        return f"{self.name} ({self.language})"


# =========================
# MOVIE MODEL
# =========================

class Movie(models.Model):

    title = models.CharField(max_length=200)

    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        default=1
    )

    language = models.CharField(
        max_length=20,
        choices=Genre.LANGUAGE_CHOICES,
        default='telugu'
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=100
    )

    description = models.TextField(blank=True)

    # YouTube trailer id
    trailer_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title


# =========================
# THEATER MODEL
# =========================

class Theater(models.Model):

    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# =========================
# SEAT MODEL
# =========================

class Seat(models.Model):

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)

    seat_number = models.CharField(max_length=10)

    status = models.CharField(
        max_length=20,
        choices=[
            ("available", "Available"),
            ("reserved", "Reserved"),
            ("booked", "Booked"),
        ],
        default="available"
    )

    reserved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.movie.title} - {self.seat_number}"


# =========================
# BOOKING MODEL
# =========================

class Booking(models.Model):

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)

    number_of_tickets = models.IntegerField()

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    booking_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.movie.title} - {self.number_of_tickets} tickets"