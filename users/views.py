from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializer, userNotificationSerializer
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime
from backend.settings import JWT_SECRET
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
import random
from django.conf import settings
from .models import User, Otp, FCMToken
from venues.models import VenueBookings
from venues.serializers import VenueBookingsSerializer
from .decorator import user_jwt_required
from .authenticate import check_user_jwt, check_phone_already_exists, check_email_already_exists, check_username_already_exists
from venues.constant import CANCELLED, REJECTED, ACCEPTED, REQUESTED
from app_admin.models import UserNotification
from django.contrib.auth.hashers import make_password


# razorpay 
import razorpay
import json
from django.conf import settings
razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY, settings.RAZOR_SECRET_KEY))
from .constant import PaymentStatus
from .models import RazorPayment
from .serializers import RazorPaymentSerializer
from rest_framework.parsers import MultiPartParser

# Create your views here.

class Register(APIView):
    def post(self, request):
        player_username = request.data['player_username']
        email = request.data['email']
        phone = request.data['phone']
        
        if User.objects.filter(player_username=player_username).exists():
            return Response({'error' : 'username already exist'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error' : 'email already exist'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(phone=phone).exists():
            return Response({'error' : 'phone already exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        user = User.objects.filter(email=email).first()
        
        # send otp to email 
        generate_otp = str(random.randint(1000,9999))
        otp = Otp.objects.create(user_id=user , otp_type='email', otp=generate_otp)
        otp.save()
        
        subject = 'PLAYOFF REGISTER VERIFICATION'
        message = f'hi this your otp {generate_otp} use your OTP to verify the registration'
        from_email = settings.EMAIL_HOST_USER
        email_to = [email]
        send_mail(subject, message, from_email, email_to, fail_silently=False)
        
        return Response(serializer.data)    
    
class verify_email(APIView):
    def post(self, request):
        email = request.data['email']
        user_otp = request.data['email_otp']
        
        if email and user_otp:
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({'error' : 'email not found register again'}, status=status.HTTP_401_UNAUTHORIZED)
            email_otp = Otp.objects.filter(user_id=user, otp_type='email').first()
            
            if email_otp.otp == user_otp:
                user.verified = True
                user.save()
                serializer = UserSerializer(user)
                return Response(serializer.data)    
            else:
                return Response({'error' : 'incorrect otp'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error' : 'email not found register again'}, status=status.HTTP_401_UNAUTHORIZED)
        
        
class SendEmailOtp(APIView):
    def post(self, request):
        email = request.data['email']
        email_otp = str(random.randint(1000,9999))
        
        user = User.objects.filter(email=email).first()
        if user is None:
            return Response({'error' : 'email not registered'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.verified:
            return Response({'error' : 'email already verified'}, status=status.HTTP_409_CONFLICT)
        
        user_otp = Otp.objects.filter(user_id=user).first()
            
        if user_otp is None:
            user_otp = Otp.objects.create(user_id=user, otp_type='email', otp=email_otp)
            user_otp.save()
        else:
            user_otp.otp = email_otp
            user_otp.save()
        
        subject = 'PLAYOFF REGISTER VERIFICATION'
        message = f'hi this your otp {email_otp} use your OTP to verify the registration'
        from_email = settings.EMAIL_HOST_USER
        email_to = [email]
        send_mail(subject, message, from_email, email_to, fail_silently=False)
        return Response({'message' : 'otp send to your email'})
        
            
    
class Login(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        
        user = User.objects.filter(email=email).first()
        if user is None or not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.is_active is False:
            return Response({'error': 'user blocked'}, status=status.HTTP_400_BAD_REQUEST)
        
        auth = authenticate(request, email=email, password=password)
        login(request, auth)
        
        payload = {
            'id' : user.id,
            'email' : user.email,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=30),
            'iat' : datetime.datetime.utcnow()       
        }
        token = jwt.encode(payload,  JWT_SECRET, algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token,  httponly=True)

        response.data =  {
            'jwt' : token,
            'message' : 'login success',
        }
        return response
            

class GetUser(APIView):
    def get(self, request):
        try:
            token = request.headers.get('Authorization')
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user = User.objects.filter(id=payload['id']).first()
            
            if not user.is_active:
                return Response({'error': 'user blocked'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = UserSerializer(user)
            return Response(serializer.data)
        
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('JWT token has expired')

        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid JWT token')
        
        
class SaveFCMToken(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        fcm_token = request.data.get('fcm_token', None)
        
        if not fcm_token:
            return Response({'error':'no fcm token'}, status=status.HTTP_400_BAD_REQUEST)
        
        if FCMToken.objects.filter(user_id=user).exists():
            user_token = FCMToken.objects.filter(user_id=user).first()
            if user_token.fcm_token != fcm_token:
                user_token.fcm_token = fcm_token
                user_token.save()
                return Response('user token saved')
            else:
                return Response('user token saved')
        else:
            new_token = FCMToken.objects.create(user_id=user, fcm_token=fcm_token)
            new_token.save()
            return Response('token saved success') 

        
class UserLogout(APIView):
    def post(self, request):
        user_id = request.data['user_id']
        user = User.objects.get(id=user_id)
        
        response = Response()
        response.delete_cookie('jwt')
        notification_token = FCMToken.objects.filter(user_id=user).first()
        if notification_token:
            notification_token.delete()
            notification_token.save()
        response.data = {
            'message' : 'logout success'
        }        
        return response
    
    
class SendOtp(APIView):
    def post(self, request):
        email = request.data['email']
        email_otp = str(random.randint(1000,9999))
        
        user = User.objects.filter(email=email).first()
        if user is None:
            return Response({'error' : 'email not registered'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({'error' : "can't send otp to this email"}, status=status.HTTP_401_UNAUTHORIZED)
        user_otp = Otp.objects.filter(user_id=user).first()
            
        if user_otp is None:
            user_otp = Otp.objects.create(user_id=user, otp_type='email', otp=email_otp)
            user_otp.save()
        else:
            user_otp.otp = email_otp
            user_otp.save()
        
        subject = 'PLAYOFF CHANGE PASSWORD'
        message = f'hi this your otp {email_otp} use this OTP to change password'
        from_email = settings.EMAIL_HOST_USER
        email_to = [email]
        send_mail(subject, message, from_email, email_to, fail_silently=False)
        return Response({'message' : 'otp send to your email'})
    

class ChangePassword(APIView):
    def post(self, request):
        email = request.data['email']
        otp = request.data['otp']
        new_password = request.data['new_password']
    
        user = User.objects.filter(email=email).first()
        if user is None:
            return Response({'error' : 'email not registered'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({'error' : "invalid email"}, status=status.HTTP_401_UNAUTHORIZED)
        
        user_otp = Otp.objects.filter(user_id=user).first()
        
        if user_otp is None:
            return Response({'error' : 'otp verification failed'}, status=status.HTTP_400_BAD_REQUEST)
        
        if otp == user_otp.otp:
            user.set_password(new_password)
            user.save()
            return Response({'success' : 'password changed'})
        else:
            return Response({'error' : 'incorrect otp'}, status=status.HTTP_400_BAD_REQUEST)
        
class getBookings(APIView):
    def get(self, request):
        try:
            token = request.headers.get('Authorization')
            user = check_user_jwt(token)
            bookings = VenueBookings.objects.filter(user_id=user).order_by('-id')
            serializer = VenueBookingsSerializer(bookings, many=True)
            return Response(serializer.data)
        except:
            return Response({'error' : 'something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class CancelBooking(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        booking_id = request.data['booking_id']
        booking = VenueBookings.objects.get(id=booking_id, user_id=user)

        if booking and booking.booking_status != REJECTED:
            booking.booking_status = CANCELLED
            booking.save()
            return Response('booking cancelled')
        else:
            return Response('failed to cancel booking', status=status.HTTP_400_BAD_REQUEST)
        
        

class startRazorpayment(APIView):
    def post(self, request):
        amount = request.data['amount']
        name = request.data['name']
        
        payment = razorpay_client.order.create(
            {"amount": float(amount) * 100, "currency" : "INR", "payment_capture":"1" }
        )
        order = RazorPayment.objects.create(order_product=name, order_amount=amount, order_payment_id=payment['id'])
        
        print(order)
        serializer = RazorPaymentSerializer(order)
        
        data = {
            "payment": payment,
            "order": serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)
    
    
class handle_payment_success(APIView):
    def post(self, request):
        razorpay_payment_id = request.data['razorpay_payment_id']
        razorpay_order_id = request.data['razorpay_order_id']
        razorpay_signature = request.data['razorpay_signature']
        booking_id = request.data['booking_id']
                
        order = RazorPayment.objects.get(order_payment_id=razorpay_order_id)
        
        data = {
            'razorpay_order_id' : razorpay_order_id,
            'razorpay_payment_id' : razorpay_payment_id,
            'razorpay_signature' : razorpay_signature
        }
        check = razorpay_client.utility.verify_payment_signature(data)
        if check is None:
            print("Redirect to error url or error page")
            return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
        
        booking = VenueBookings.objects.get(id=booking_id)
        booking.payment_status = True
        booking.save()
        order.isPaid = True
        order.save()
        return Response({'message': 'payment successfully received!'})
    
    
class getUserNotification(APIView):   
    def get(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        
        user_notifications = UserNotification.objects.filter(user_id=user).order_by('-id')
        serializer = userNotificationSerializer(user_notifications, many=True)
        return Response(serializer.data)
    
    # read notification 
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        user_notifications = UserNotification.objects.filter(user_id=user)
        
        for notification in user_notifications:
            notification.seen = True 
            notification.save()   
            
        return Response('seen marked')
    
class UpdateUserProfile(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        phone = request.data['phone']
        
        if first_name and first_name != user.first_name:
            user.first_name = first_name
            user.save()
        
        if last_name and last_name != user.last_name:
            user.last_name = last_name
            user.save()
            
        if phone and phone != user.phone:
            phone_already_exists = check_phone_already_exists(phone)
            if not phone_already_exists:
                user.phone = phone
                user.save()
            else:
                return Response({'error' : 'phone already exist'}, status=status.HTTP_409_CONFLICT)
        
        serilizer = UserSerializer(user)
        return Response(serilizer.data)
    

class OtpChangeEmail(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        new_email = request.data['new_email']
        email_otp = str(random.randint(1000,9999))
        
        if check_email_already_exists(new_email):
            return Response({'error' : 'email already exist'}, status=status.HTTP_409_CONFLICT)
        
        user_otp = Otp.objects.filter(user_id=user).first()
            
        if user_otp is None:
            user_otp = Otp.objects.create(user_id=user, otp_type='email', email=new_email, otp=email_otp)
            user_otp.save()
        else:
            user_otp.otp = email_otp
            user_otp.email = new_email
            user_otp.save()
        
        subject = 'PLAYOFF CHANGE EMAIL'
        message = f'hi this your otp {email_otp} use this OTP to change your email'
        from_email = settings.EMAIL_HOST_USER
        email_to = [new_email]
        send_mail(subject, message, from_email, email_to, fail_silently=False)
        return Response({'message' : 'otp send to your email'})
    
    
class ChangeEmail(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        
        new_email = request.data['new_email']
        otp = request.data['otp']
        
        user_otp = Otp.objects.get(user_id=user, email=new_email)
        
        if user_otp and user_otp.otp == otp:
            user.email = new_email
            user.save()
            serializer = UserSerializer(user)
            user_otp.delete()
            return Response(serializer.data)
        else:
            return Response({'error': 'incorrect otp'}, status=status.HTTP_401_UNAUTHORIZED)
        
        
class SentOtpChangePassword(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        email_otp = str(random.randint(1000,9999))
        
        user_otp = Otp.objects.filter(user_id=user).first()
            
        if user_otp is None:
            user_otp = Otp.objects.create(user_id=user, otp_type='email', email=user.email, otp=email_otp)
            user_otp.save()
        else:
            user_otp.otp = email_otp
            user_otp.email = user.email 
            user_otp.save()
        
        subject = 'PLAYOFF CHANGE PASSWORD'
        message = f'hi this your otp {email_otp} use this OTP to change password'
        from_email = settings.EMAIL_HOST_USER
        email_to = [user.email]
        send_mail(subject, message, from_email, email_to, fail_silently=False)
        return Response('otp sent successfully')
        
class UserChangePassword(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        
        otp = request.data['otp']
        password = request.data['password']
        
        user_otp = Otp.objects.filter(user_id=user).first()
        
        if user_otp and user_otp.otp == otp:
            hashed_password = make_password(password)
            user.password = hashed_password
            user.save()
            return Response('password changed successfully')
        else:
            return Response({'error': 'incorrect otp'}, status=status.HTTP_401_UNAUTHORIZED)
        
        
class UserChangeProfile(APIView):
    parser_classes = [MultiPartParser]
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        
        print(request.data)
        username = request.data['username']
        profile_image = request.FILES.get('file', None)
        skill = request.data['skill']
        
        if username and username != user.player_username:
            if check_username_already_exists(username):
                return Response({'error' : 'username already exist'}, status=status.HTTP_409_CONFLICT)
            else:
                user.player_username = username
        
        if profile_image and profile_image != user.profile_img:
            user.profile_img = profile_image
            
        if skill and skill != user.skill_level:
            user.skill_level = skill
            
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)
        

    
class check_username(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        user = check_user_jwt(token)
        player_username = request.data['username']
        
        if player_username != user.player_username:
            if User.objects.filter(player_username=player_username).exists():
                return Response({'error' : 'username already exist'}, status=status.HTTP_409_CONFLICT)
            else:
                return Response({'success' : 'available'})
        else:
            return Response({'success' : 'available'})
        
        
# class check_email(APIView):
#     def post(self, request):
#         email = request.data['email']
#         if User.objects.filter(email=email).exists():
#             return Response({'error' : 'email already exist'}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({'success' : 'available'})
        
        
# class check_phone(APIView):
#     def post(self, request):
#         phone = request.data['phone']
#         if User.objects.filter(phone=phone).exists():
#             return Response({'error' : 'phone already exist'}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({'success' : 'available'})
