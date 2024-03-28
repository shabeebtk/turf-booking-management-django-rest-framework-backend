from django.db import models
from turf_owner.models import Owners
from users.models import User
# Create your models here.


class Venues(models.Model):
    owner_id = models.ForeignKey(Owners, on_delete=models.CASCADE)
    venue_name = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    location = models.URLField(max_length=200)
    about_venue = models.TextField()
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    created_at = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=False)
    
    STATUS_CHOICES = [
        ('requested', 'requested'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected')
    ]
    venue_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    
    def __str__(self) -> str:
        return self.venue_name
    

class VenuePrice(models.Model):
    SIDE_CHOICES = [
        ('5-aside', '5-aside'),
        ('6-aside', '6-aside'),
        ('7-aside', '7-aside'),
        ('8-aside', '8-aside'),
        ('9-aside', '9-aside'),
        ('10-aside', '10-aside'),
        ('11-aside', '11-aside')
    ]
    venue_id = models.ForeignKey(Venues, on_delete=models.CASCADE, related_name='venue_prices')
    side = models.CharField(max_length=20, choices=SIDE_CHOICES)
    day_price = models.DecimalField(max_digits=10, decimal_places=2)
    night_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self) -> str:
        return f'{self.venue_id.venue_name} - { self.side} - {self.day_price} - {self.night_price}'
    
    
class VenueImages(models.Model):
    venue_id = models.ForeignKey(Venues, on_delete=models.CASCADE, related_name='venue_images')
    image = models.ImageField(upload_to='venue_images/', null=True)
    
    def __str__(self) -> str:
        return self.venue_id.venue_name
    
    
class VenueFacilities(models.Model):
    venue_id = models.ForeignKey(Venues, on_delete=models.CASCADE, related_name='venue_facilities')
    facility = models.CharField()
    
    def __str__(self) -> str:
        return f'{self.venue_id.venue_name} - {self.facility}'
    
    
class VenueBookings(models.Model):
    venue_id = models.ForeignKey(Venues, on_delete=models.CASCADE, related_name='venue_bookings')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='venue_bookings')
    court = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField()
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    
    STATUS_CHOICES = [
        ('requested', 'requested'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected'),
        ('cancelled', 'cancelled'),
        ('booked', 'booked')
    ]
    booking_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user_id.email} - {self.venue_id.venue_name} - {self.court}'
    
    
    
        