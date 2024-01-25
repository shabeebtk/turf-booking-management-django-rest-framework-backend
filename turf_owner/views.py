from django.shortcuts import render
from .serializers import OwnerSerializer
from datetime import datetime
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime
from backend.settings import JWT_SECRET
from rest_framework.permissions import IsAuthenticated
from .models import Owners
import random
from django.conf import settings
from django.core.mail import send_mail
from .models import OwnerOtp
from django.contrib.auth.hashers import check_password
from venues.models import Venues, VenueBookings
from venues.serializers import CheckVenueSerializer, VenueBookingsSerializer
from venues.constant import ACCEPTED, REQUESTED, REJECTED, CANCELLED
from django.db.models import Q
from app_admin.models import UserNotification
from game.notification import send_notification
# Create your views here.

class OnwerRegister(APIView):
    def post(self, request):
        print(request.data)
        owner_email = request.data['owner_email']
        owner_phone = request.data['owner_phone']
        
        if Owners.objects.filter(owner_email=owner_email).exists():
            return Response({"error" : "this email already registered"}, status=status.HTTP_400_BAD_REQUEST)
    
        if Owners.objects.filter(owner_phone=owner_phone).exists():
            return Response({"error" : "phone number already registered"}, status=status.HTTP_400_BAD_REQUEST)
    

        serailizer = OwnerSerializer(data= request.data)
        serailizer.is_valid(raise_exception=True)
        serailizer.save()
        owner = Owners.objects.filter(owner_email=owner_email).first()
        
        generate_otp = str(random.randint(1000,9999))
        otp = OwnerOtp.objects.create(owner_id=owner , otp_type='email', otp=generate_otp)
        otp.save()
        
        subject = 'PLAYOFF TURF OWNER REGISTER VERIFICATION'
        message = f'hi this your otp {generate_otp} use your OTP to verify the registration'
        from_email = settings.EMAIL_HOST_USER
        email_to = [owner_email]
        print(generate_otp)
        send_mail(subject, message, from_email, email_to, fail_silently=False)
        return Response(serailizer.data)
    
    
class VerifyOwnerEmail(APIView):
    def post(self, request):
        email = request.data['owner_email']
        owner_otp = request.data['email_otp']
        print(owner_otp)
        if email and owner_otp:
            print('hwllo')
            owner = Owners.objects.filter(owner_email=email).first()
            print(owner)
            email_otp = OwnerOtp.objects.filter(owner_id = owner,otp_type='email').first()
            print(email_otp.otp, owner_otp, 'otp--------')
            if email_otp.otp == owner_otp:
                owner.owner_verified = True
                owner.save()
                serializer = OwnerSerializer(owner)
                return Response(serializer.data)    
            else:
                return Response({'error' : 'incorrect otp'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error' : 'email not found register again'}, status=status.HTTP_400_BAD_REQUEST)
       
       
class OwnerLogin(APIView):
    def post(self, request):
        email = request.data['owner_email']
        password = request.data['owner_password']
        
        owner = Owners.objects.filter(owner_email=email).first()
        print(owner)
        if owner is None:
            return Response({'error' : 'invalid details'}, status=status.HTTP_400_BAD_REQUEST)
            
        if not check_password(password, owner.owner_password):
            return Response({'error' : 'invalid details'}, status=status.HTTP_400_BAD_REQUEST)
        
        payload = {
            'id' : owner.id,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            'iat' : datetime.datetime.utcnow()       
        }
        
        token = jwt.encode(payload,  JWT_SECRET, algorithm='HS256')
        response = Response()
        response.set_cookie(key='ownerjwt', value=token,  httponly=True)
        response.data =  {
            'ownerjwt' : token,
            'message' : 'login success'
        }
        return response
            
            
class GetOwner(APIView):
    def get(self, request):
        try:
            token = request.headers.get('Authorization')
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            owner = Owners.objects.filter(id=payload['id']).first()
            serializer = OwnerSerializer(owner)
            return Response(serializer.data)
        
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('JWT token has expired')

        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid JWT token')
        
        
        
class OwnerLogout(APIView):
    def post(self,request):
        response = Response()
        response.delete_cookie('ownerjwt')
        response.data = {
            'message' : 'logout success'
        }
        return response
    
    
    
class CheckOnwerHaveVenue(APIView):
    def post(self, request):
        owner_email = request.data['email']
        owner = Owners.objects.filter(owner_email=owner_email).first()
        venue = Venues.objects.filter(owner_id=owner).first()
        
        if venue is not None:
            serializer = CheckVenueSerializer(venue)
            return Response(serializer.data)
        else:
            return Response({"error" : "venue not found"})
        
        
class GetBookingRequest(APIView):
    def get(self, request):
        try:
            token = request.headers.get('Authorization')
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            owner = Owners.objects.get(id=payload['id'])
            owner_venue = Venues.objects.get(owner_id=owner)
            
            print(owner_venue)
            if not owner:
                return Response({'error': 'authuntication failed'}, status=status.HTTP_400_BAD_REQUEST)
            
            booking_requests = VenueBookings.objects.filter(venue_id=owner_venue, booking_status=REQUESTED).order_by('-id')
            serializer = VenueBookingsSerializer(booking_requests, many=True)
            return Response(serializer.data)
        except:
            return Response({'error' : 'error occured while getting the booking requests'}, status=status.HTTP_400_BAD_REQUEST)
            
            
class AcceptBookRequest(APIView):
    def post(self, request):
        try:
            token = request.headers.get('Authorization')
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            owner = Owners.objects.get(id=payload['id'])
            
            if not owner:
                return Response({'error': 'authuntication failed'}, status=status.HTTP_400_BAD_REQUEST)
            
            booking_id = request.data['booking_id']
            venue_id = request.data['venue_id']
            court = request.data['court']
            date = request.data['date']
            time = request.data['time']
            current_date_time = timezone.now()
    
            if VenueBookings.objects.filter(venue_id=venue_id, court=court, date=date, time=time, booking_status=ACCEPTED).exists():
                return Response({'message' : 'slot already booked'}, status=status.HTTP_208_ALREADY_REPORTED)
            booking = VenueBookings.objects.get(id=booking_id)
            
            if booking.date < current_date_time.date() or booking.date == current_date_time.date() and booking.time < current_date_time.time():
                return Response({'message' : 'request expired'}, status=status.HTTP_408_REQUEST_TIMEOUT)
            
            if booking and booking.booking_status != REJECTED and booking.booking_status != CANCELLED:
                booking.booking_status = ACCEPTED
                booking.save()
                
                UserNotification.objects.create(
                        user_id=booking.user_id,
                        title='venue request accepted',
                        body=f'{booking.user_id.player_username}, your venue request at {booking.venue_id.venue_name} has been accepted please make the payment to book the venue'
                    ).save()
                send_notification(booking.user_id.id, 'venue booking accepted', f'your venue request at {booking.venue_id.venue_name} has been accepted please make the payment to book the venue')
                return Response({'booking request accepted'})

            else:
                return Response({'error' : 'something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error' : 'something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
        
class DeclineBookRequest(APIView):
    def post(self, request):
        try:
            token = request.headers.get('Authorization')
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            owner = Owners.objects.get(id=payload['id'])
            
            if not owner:
                return Response({'error': 'authuntication failed'}, status=status.HTTP_400_BAD_REQUEST)
            
            booking_id = request.data['booking_id']
            booking = VenueBookings.objects.get(id=booking_id)
            if booking and booking.booking_status != ACCEPTED:
                booking.booking_status = REJECTED
                booking.save()
                UserNotification.objects.create(
                        user_id=booking.user_id,
                        title='venue request rejected',
                        body=f'{booking.user_id.player_username}, sorry your venue request at {booking.venue_id.venue_name} has been rejected by the turf owners'
                    ).save()
                return Response({'booking request rejected'})
        except:
            return Response({'error' : 'something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class GetBookings(APIView):
    def get(self, request):
        try:
            token = request.headers.get('Authorization')
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            owner = Owners.objects.get(id=payload['id'])
            owner_venue = Venues.objects.get(owner_id=owner)
            
            print(owner_venue)
            if not owner:
                return Response({'error': 'authuntication failed'}, status=status.HTTP_400_BAD_REQUEST)
            
            booking_requests = VenueBookings.objects.filter(
                Q(venue_id=owner_venue, booking_status=ACCEPTED) | Q(venue_id=owner_venue, booking_status=CANCELLED) | Q(venue_id=owner_venue, booking_status=REJECTED)
                ).order_by('-id')
            serializer = VenueBookingsSerializer(booking_requests, many=True)
            return Response(serializer.data)
        except:
            return Response({'error' : 'error occured while getting the booking requests'}, status=status.HTTP_400_BAD_REQUEST)
        
        