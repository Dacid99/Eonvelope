from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.middleware.csrf import get_token
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.permissions import AllowAny

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        remember = request.data.get('remember')
        
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request=request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            if remember:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            else:
                request.session.set_expiry(0)
            
            csrf_token = get_token(request)
            
            return Response({
                'detail': 'Login successful',
                'csrf_token': csrf_token
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
            
            
class LogoutView(APIView):
    def post(self, request):
        logout(request)
        
        return Response({
            'detail': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
        
class CSRFCookieView(APIView):
    permission_classes = [AllowAny]
    
    @ensure_csrf_cookie
    def get(self, request):
        csrf_token = get_token(request)
        return Response({
            'csrf_token': csrf_token
        })