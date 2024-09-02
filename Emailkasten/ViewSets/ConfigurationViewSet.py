from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, Http404
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from ..Models.ConfigurationModel import ConfigurationModel
from ..Serializers import ConfigurationSerializer
import os

class ConfigurationViewSet(viewsets.ModelViewSet):
    queryset = ConfigurationModel.objects.all()
    serializer_class = ConfigurationSerializer
    permission_classes = [IsAdminUser]
