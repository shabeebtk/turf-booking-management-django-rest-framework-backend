from rest_framework.exceptions import AuthenticationFailed
import jwt
from .serializers import AdminSerializers
from backend.settings import JWT_SECRET
from users.models import User

def admin_token_required(func):
    def wrapper(request, *args, **kwargs):
        token = request.headers.get('Authorization')
        
        print(token)
        if not token:
            raise AuthenticationFailed('Authorization header is missing')

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            admin = User.objects.filter(id=payload['id'], is_superuser=True).first()

            if not admin:
                raise AuthenticationFailed('User not authorized as admin')

            serializer = AdminSerializers(admin)
            return func(request, admin, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('JWT token has expired')

        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid JWT token')

    return wrapper