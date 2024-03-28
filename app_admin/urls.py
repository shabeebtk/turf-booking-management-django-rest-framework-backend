from django.urls import path
from .views import *

urlpatterns = [
    path('login', AdminSignin.as_view()),
    path('get_admin', GetAdmin.as_view()),
    path('admin_logout', AdminLogout.as_view()),
    path('users', GetAllUsers.as_view()),
    path('venues', GetAllVenues.as_view()),
    path('block_unblock_user', BlockUnblockUser.as_view()),
    
    # venues 
    path('requested_venues', GetAllVenuRequests.as_view()),
    path('view_requested_venue', GetVenueDetails.as_view()),
    path('accept_requested_venue', AcceptVenueRequest.as_view()),
    path('decline_requested_venue', DeclineVenueRequest.as_view()),
    
    path('dashboard_details', AdminDashboard.as_view())
    
]
