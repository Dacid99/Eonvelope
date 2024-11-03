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

from ..Filters.AttachmentsFilter import AttachmentFilter
from ..Models.AttachmentModel import AttachmentModel
from ..Serializers.AttachmentSerializers.AttachmentSerializer import \
    AttachmentSerializer


class AttachmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AttachmentModel.objects.all()
    serializer_class = AttachmentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AttachmentFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['file_name', 'datasize', 'email__datetime', 'created']
    ordering = ['id']

    def get_queryset(self):
        return AttachmentModel.objects.filter(email__account__user = self.request.user)


    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        attachment = self.get_object()
        fileName = attachment.file_name
        filePath = attachment.file_path

        if not os.path.exists(filePath):
            raise Http404("Attachment file not found")
        
        response = FileResponse(open(filePath, 'rb'), as_attachment=True, filename=fileName)
        return response


    @action(detail=True, methods=['post'], url_path='toggle_favorite')
    def toggle_favorite(self, request, pk=None):
        attachment = self.get_object()
        attachment.is_favorite = not attachment.is_favorite
        attachment.save()
        return Response({'status': 'Attachment marked as favorite'})
    
    
    @action(detail=False, methods=['get'], url_path='favorites')
    def favorites(self, request):
        favoriteAttachments = AttachmentModel.objects.filter(is_favorite=True)
        serializer = self.get_serializer(favoriteAttachments, many=True)
        return Response(serializer.data)