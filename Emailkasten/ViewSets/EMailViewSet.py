'''
    Emailkasten - a open-source self-hostable email archiving server
    Copyright (C) 2024  David & Philipp Aderbauer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from ..Models.EMailModel import EMailModel
from ..Serializers import EMailSerializer
from ..Filters.EMailFilter import EMailFilter
import os

class EMailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EMailModel.objects.all()
    serializer_class = EMailSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = EMailFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['datetime', 'email_subject', 'datasize', 'created']
    ordering = ['id']

    def get_queryset(self):
        return EMailModel.objects.filter(account__user = self.request.user)
    
    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        email = self.get_object()
        filePath = email.eml_filepath
        if filePath:
            if os.path.exists(filePath):
                fileName = os.path.basename(filePath)
                response = FileResponse(open(filePath, 'rb'), as_attachment=True, filename=fileName)
                return response
            else:
                raise Http404("EMl file not found")
        else:
            raise Http404("No EML file available")            
    
    
    @action(detail=True, methods=['get'], url_path='prerender')
    def prerender(self, request, pk=None):
        email = self.get_object()
        filePath = email.prerender_filepath
        if filePath:
            if os.path.exists(filePath):
                fileName = os.path.basename(filePath)
                response = FileResponse(open(filePath, 'rb'), as_attachment=True, filename=fileName)
                return response
            else:
                raise Http404("Prerender image file not found")
        else:
            raise Http404("No prerender image file available")
        
    
    @action(detail=True, methods=['post'], url_path='toggle_favorite')
    def toggle_favorite(self, request, pk=None):
        email = self.get_object()
        email.is_favorite = not email.is_favorite
        email.save()
        return Response({'status': 'Email marked as favorite'})
    
    
    @action(detail=False, methods=['get'], url_path='favorites')
    def favorites(self, request):
        favoriteEmails = EMailModel.objects.filter(is_favorite=True)
        serializer = self.get_serializer(favoriteEmails, many=True)
        return Response(serializer.data)