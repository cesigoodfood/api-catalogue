from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings

class MicroserviceUser:
    def __init__(self, payload):
        self.id = payload.get('id')
        self.role = payload.get('role')
        self.is_authenticated = True

class MicroserviceJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
            
        token = auth_header.split(' ')[1]
        public_key = getattr(settings, 'JWT_PUBLIC_KEY', None)
        
        if not public_key:
            return None
            
        try:
            payload = jwt.decode(token, public_key, algorithms=['RS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.PyJWTError as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')
            
        return (MicroserviceUser(payload), token)
