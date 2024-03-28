from django.urls import path
from .views import *
from venues.views import AddVenue, SaveVenueImages

urlpatterns = [
    path('register', OnwerRegister.as_view()),
    path('verify_owner_email', VerifyOwnerEmail.as_view()),
    path('login', OwnerLogin.as_view()),
    path('get_owner', GetOwner.as_view()),
    path('logout', OwnerLogout.as_view()),
    
    path('add_venue', AddVenue.as_view()),
    path('save_images', SaveVenueImages.as_view()),
    path('check_venue', CheckOnwerHaveVenue.as_view()),
    path('bookings/requests', GetBookingRequest.as_view()),
    path('bookings/accept', AcceptBookRequest.as_view()),
    path('bookings/decline', DeclineBookRequest.as_view()),
    path('bookings', GetBookings.as_view()),
]
