from rest_framework.exceptions import AuthenticationFailed
import jwt
from backend.settings import JWT_SECRET
from .models import User

def check_admin_jwt(token):
    if not token:
        raise AuthenticationFailed('Authorization header is missing')
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = User.objects.filter(id=payload['id'], is_superuser=True).first()

        if not user:
            raise AuthenticationFailed('User not authorized')
        return user            
    
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('JWT token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid JWT token')
    


        
