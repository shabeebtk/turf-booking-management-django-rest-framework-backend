from django.shortcuts import render
from .models import Venues, VenueFacilities, VenueImages, VenuePrice, VenueBookings
from .serializers import VenueSerailizer, VenueFacilitiesSerializer, VenueImageSerializer, VenuePriceSerializer, AddVenueSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt, datetime
from backend.settings import JWT_SECRET
from turf_owner.models import Owners
import requests
from users.models import User
from django.shortcuts import get_object_or_404
from jwt.exceptions import ExpiredSignatureError
# Create your views here.

class AddVenue(APIView):
    def is_valid_link(self, url):
        try:
            response = requests.head(url, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
        
    def post(self, request):        
        venue_prices = request.data['venue_price']
        venue_facilities = request.data['venue_facilities']
        serializer = AddVenueSerializer(data=request.data)
        
        location_link = request.data['location']
        
        if not self.is_valid_link(location_link):
            print('working')
            return Response({"message": "The location link is not valid"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            
        venue_id = serializer.data['id']
        venue = Venues.objects.filter(id=venue_id).first()
        
        for facility in venue_facilities: 
            venue_facility = VenueFacilities.objects.create(venue_id=venue, facility=facility)
            venue_facility.save()
            
        for data in venue_prices:
            venue_price = VenuePrice.objects.create(venue_id=venue, side=data['aside'], day_price=data['dayPrice'], night_price=data['nightPrice'])
            venue_price.save()
            
        print(serializer.data)
            
        return Response(serializer.data)
    
    
class SaveVenueImages(APIView):
    def post(self, request):        
        venue_id = request.data['venue_id']
        all_images = request.FILES
        venue = Venues.objects.filter(id=venue_id).first()
        
        if venue is not None:
            for i in range(len(all_images)):
                venue_image = VenueImages.objects.create(venue_id=venue, image=all_images[f'images[{i}]'])
                venue_image.save()
            return Response('venue images saved successfully')
        else:
            return Response('Venue not found', status=status.HTTP_404_NOT_FOUND)


class GetActiveVenues(APIView):
    def get(self, request):
        all_venues = Venues.objects.filter(active=True, venue_status='accepted')
        serializer = VenueSerailizer(all_venues, many=True)
        return Response(serializer.data)
    
    
class GetSelectedCityVenues(APIView):
    def post(self, request):
        city = request.data['city']
        print(city)
        all_venues = Venues.objects.filter(active=True, venue_status='accepted', city__icontains=city)
        serializer = VenueSerailizer(all_venues, many=True)
        return Response(serializer.data)
    
    
class BookVenue(APIView):
    def post(self, request):
        try:
            token = request.headers.get('Authorization')
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user = User.objects.get(id=payload['id'])
            
            if not user.is_active:
                return Response({'error': 'user blocked'}, status=status.HTTP_400_BAD_REQUEST)
            
            venue_id = request.data['venue_id']
            court = request.data['court']   
            date = request.data['date']
            time = request.data['time']
            duration = request.data['duration']
            price_per_hour = request.data['price_per_hour']
            total_price = request.data['total_price']
            
            venue = Venues.objects.get(id=venue_id)
            venue_price = VenuePrice.objects.get(venue_id=venue, side=court)
            
            print(price_per_hour, total_price)
            if time > '18:00':
                price_per_hour = venue_price.night_price
                total_price = float(duration) * float(price_per_hour)
            
            if VenueBookings.objects.filter(venue_id=venue, court=court, date=date, time=time, booking_status='accepted').exists():
                return Response({'message' : 'venue already booked selected time'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            
            if venue:
                book_venue = VenueBookings.objects.create(venue_id=venue, 
                                                        user_id=user, court=court,
                                                        date=date, time=time, 
                                                        duration=duration,
                                                        price_per_hour=price_per_hour, total_price=total_price)
                book_venue.save()
                return Response('venue booking success')
            
        except ExpiredSignatureError:
            return Response({'token expired'}, status=status.HTTP_401_UNAUTHORIZED)
        
        
        
        