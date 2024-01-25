from rest_framework.exceptions import AuthenticationFailed
import jwt
from backend.settings import JWT_SECRET
from .models import User

def user_jwt_required(func):
    def wrapper(request, *args, **kwargs):
        print(request.headers)
        token = request.headers.get('Authorization')
        print(token)
        if not token:
            raise AuthenticationFailed('Authorization header is missing')
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user = User.objects.get(id=payload['id'])
            
            if not user:
                raise AuthenticationFailed('User not authorized')
            
            return func(request, user, **args, **kwargs)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('JWT token has expired')

        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid JWT token')
        
    return wrapper