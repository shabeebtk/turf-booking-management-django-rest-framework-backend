from rest_framework.exceptions import AuthenticationFailed
import jwt
from backend.settings import JWT_SECRET
from .models import User

def check_user_jwt(token):
    if not token:
        raise AuthenticationFailed('Authorization header is missing')
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = User.objects.get(id=payload['id'])

        if not user:
            raise AuthenticationFailed('User not authorized')
        return user            
    
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('JWT token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid JWT token')
    
def check_phone_already_exists(phone):
    if User.objects.filter(phone=phone).exists():
        return True
    else:
        return False
    
def check_email_already_exists(email):
    if User.objects.filter(email=email).exists():
        return True
    else:
        return False
    
def check_username_already_exists(username):
    if User.objects.filter(player_username=username).exists():
        return True
    else:
        return False
    
    
# class check_username(APIView):
#     def post(self, request):
#         player_username = request.data['player_username']
#         if User.objects.filter(player_username=player_username).exists():
#             return Response({'error' : 'username already exist'}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({'success' : 'available'})
        

        
