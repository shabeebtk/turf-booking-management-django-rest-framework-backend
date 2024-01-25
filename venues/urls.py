from django.urls import path
from .views import *
from app_admin.views import GetVenueDetails

urlpatterns = [
    path('all_venues', GetActiveVenues.as_view()),
    path('venue_details', GetVenueDetails.as_view()),
    path('city_venues', GetSelectedCityVenues.as_view()),
    path('book_venue', BookVenue.as_view()),
]
