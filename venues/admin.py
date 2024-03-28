from django.contrib import admin
from .models import Venues, VenueFacilities, VenueImages, VenuePrice, VenueBookings

# Register your models here.


admin.site.register(Venues)
admin.site.register(VenueFacilities)
admin.site.register(VenueImages)
admin.site.register(VenuePrice)
admin.site.register(VenueBookings)