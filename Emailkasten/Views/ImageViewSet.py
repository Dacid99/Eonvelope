# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..Filters.ImageFilter import ImageFilter
from ..Models.ImageModel import ImageModel
from ..Serializers.ImageSerializers.ImageSerializer import ImageSerializer


class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ImageModel.objects.all()
    serializer_class = ImageSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ImageFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['file_name', 'datasize', 'email__datetime', 'created', 'updated']
    ordering = ['id']

    def get_queryset(self):
        return ImageModel.objects.filter(email__account__user = self.request.user)

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        image = self.get_object()
        fileName = image.file_name
        filePath = image.file_path

        if not os.path.exists(filePath):
            raise Http404("Image file not found")
        
        response = FileResponse(open(filePath, 'rb'), as_attachment=True, filename=fileName)
        return response

    
    @action(detail=True, methods=['post'], url_path='toggle_favorite')
    def toggle_favorite(self, request, pk=None):
        image = self.get_object()
        image.is_favorite = not image.is_favorite
        image.save()
        return Response({'status': 'Image marked as favorite'})
    
    
    @action(detail=False, methods=['get'], url_path='favorites')
    def favorites(self, request):
        favoriteImages = ImageModel.objects.filter(is_favorite=True)
        serializer = self.get_serializer(favoriteImages, many=True)
        return Response(serializer.data)