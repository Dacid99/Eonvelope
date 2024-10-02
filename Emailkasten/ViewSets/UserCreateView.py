from ..Serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets
from ..permissions import IsAdminOrSelf

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.request.method in ['POST']:
            #use if here to allow blocking of the registration
            return [AllowAny()]
        elif self.request.method in ['PUT','PATCH','DELETE','GET']:
            return [IsAdminOrSelf(), IsAuthenticated()]
#        elif self.request.method in ['GET']:
#            return [IsAuthenticated()]
        return super().get_permissions()
    
    def get_queryset(self):
        return User.objects.filter(username=self.request.user.username)
