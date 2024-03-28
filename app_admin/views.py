from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime
from backend.settings import JWT_SECRET
from users.models import User
from .serializers import AdminSerializers
from users.serializers import UserSerializer
from .decorator import admin_token_required
from venues.models import Venues, VenueFacilities, VenueImages, VenuePrice, VenueBookings
from venues.serializers import VenueSerailizer
from venues.constant import ACCEPTED, REJECTED
from django.db.models import Sum
from .serializers import AdminDashboardSerializer
from .authenticate import check_admin_jwt
# Create your views here.

# admin authentications 
class AdminSignin(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']  
        admin = User.objects.filter(email=email, is_superuser=True).first()
        
        print(admin)
        if admin is None or not admin.check_password(password):
            return Response({'error' : 'invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        payload = {
            'id' : admin.id,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat' : datetime.datetime.utcnow()       
        }
        
        token = jwt.encode(payload,  JWT_SECRET, algorithm='HS256')
        response = Response()
        response.set_cookie(key='adminjwt', value=token,  httponly=True)
        response.data =  {
            'adminjwt' : token,
            'message' : 'login success'
        }
        return response
    
class GetAdmin(APIView):
    def get(self, request):
        try:
            token = request.headers.get('Authorization')
            print(token)
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            admin = User.objects.filter(id = payload['id'], is_superuser=True).first()
            print(admin)
            serializer = AdminSerializers(admin)
            return Response(serializer.data)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('JWT token has expired')
        
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid JWT token')
             
class AdminLogout(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('adminjwt')
        response.data = {
            'message' : 'logout success'
        }        
        return response
    
    
# get all users 
class GetAllUsers(APIView):
    def get(self, request):
        try:
            token = request.headers.get('Authorization')
            print(token)
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            admin = User.objects.filter(id = payload['id'], is_superuser=True).first()
            if admin:
                all_users = User.objects.filter(is_superuser=False)
                serializer = UserSerializer(all_users, many=True)
                return Response(serializer.data)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('authentication has expired')
        
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('authentication failed')
 
# block/unblock user             
class BlockUnblockUser(APIView):
    def post(self, request):
        print(request.data['Authorization'])
        user_id = request.data['user_id']
        user = User.objects.filter(id=user_id).first()
        
        print(user_id)
        if user:
            print(user.is_active, 'before')
            if user.is_active:
                user.is_active = False
            else:
                user.is_active = True
            
            user.save()
                
            print(user.is_active, 'after')
            return Response({'success' : 'user details changed'})
        else:
            return Response({'error' : 'user not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            
            
# view venue requests 
class GetAllVenuRequests(APIView):
    def get(self, request):
        requested_veneus = Venues.objects.all().order_by('-id')
        venue_serializer = VenueSerailizer(requested_veneus, many=True)
        return Response(venue_serializer.data)
        

class GetVenueDetails(APIView):
    def post(self, request):
        print(request.data)
        venue_id = request.data['venue_id']
        try:
            venue = Venues.objects.get(id=venue_id) 
            venue_serializer = VenueSerailizer(venue)
            return Response(venue_serializer.data)
        except:
            return Response({'error' : 'venue not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class AcceptVenueRequest(APIView):
    def post(self, request):
        print(request.data)
        venue_id = request.data['venue_id']
        try:
            venue = Venues.objects.get(id=venue_id)
            venue.venue_status = ACCEPTED
            venue.active = True
            venue.save()
            return Response({'success' : 'venue verified successfully'})
        except:
            return Response({'error' : 'error occurred'})
        
        
        
class DeclineVenueRequest(APIView):
    def post(self, request):
        print(request.data)

        venue_id = request.data['venue_id']
        try:
            venue = Venues.objects.get(id=venue_id)
            venue.venue_status = REJECTED
            venue.active = False
            venue.save()
            return Response({'success' : 'venue rejection done'})
        except:
            return Response({'error' : 'error occurred'})
        
        

class GetAllVenues(APIView):
    def get(self, request):
        try:
            token = request.headers.get('Authorization')
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            admin = User.objects.get(id = payload['id'], is_superuser=True)
            if admin:
                veneus = Venues.objects.filter(venue_status=ACCEPTED).order_by('-id')
                venue_serializer = VenueSerailizer(veneus, many=True)
                return Response(venue_serializer.data)
            else:
                return Response({'error' : 'user not found'}, status= status.HTTP_400_BAD_REQUEST)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('authentication has expired')
        
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('authentication failed')
                
        
        
class AdminDashboard(APIView):
    def get(self, request):
        # token = request.headers.get('Authorization')
        # admin = check_admin_jwt(token)
        total_users = User.objects.filter(is_active=True).count()
        total_venues = Venues.objects.filter(active=True).count()
        total_bookings = VenueBookings.objects.filter(booking_status=ACCEPTED).count()
        total_earnings = VenueBookings.objects.aggregate(Sum('total_price'))['total_price__sum']
        
        serializer = AdminDashboardSerializer({
            'total_users' : total_users,
            'total_venues' : total_venues,
            'total_bookings' : total_bookings,
            'total_earnings' : total_earnings,
        })
        
        return Response(serializer.data)
