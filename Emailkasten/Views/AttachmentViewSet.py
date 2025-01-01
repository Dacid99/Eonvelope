# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Module with the :class:`AttachmentViewSet` viewset."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..Filters.AttachmentFilter import AttachmentFilter
from ..Models.AttachmentModel import AttachmentModel
from ..Serializers.AttachmentSerializers.AttachmentSerializer import \
    AttachmentSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request
    from django.db.models import BaseManager


class AttachmentViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for the :class:`Emailkasten.Models.AttachmentModel.AttachmentModel`."""

    BASENAME = 'attachments'
    serializer_class = AttachmentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AttachmentFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['file_name', 'datasize', 'email__datetime', 'is_favorite', 'created', 'updated']
    ordering = ['id']

    def get_queryset(self) -> BaseManager[AttachmentModel]:
        """Filters the data for entries connected to the request user.

        Returns:
            The attachment entries matching the request user."""
        return AttachmentModel.objects.filter(email__account__user = self.request.user)


    URL_PATH_DOWNLOAD = 'download'
    URL_NAME_DOWNLOAD = 'download'
    @action(detail=True, methods=['get'], url_path=URL_PATH_DOWNLOAD, url_name=URL_NAME_DOWNLOAD)
    def download(self, request: Request, pk: int|None = None) -> FileResponse:
        """Action method downloading the attachment.

        Args:
            request: The request triggering the action.
            pk: The private key of the attachment to download. Defaults to None.

        Raises:
            Http404: If the filepath is not in the database or it doesnt exist.

        Returns:
            A fileresponse containing the requested file.
        """
        attachment = self.get_object()

        attachmentFilePath = attachment.file_path
        if not attachmentFilePath or not os.path.exists(attachmentFilePath):
            raise Http404("Attachment file not found")

        attachmentFileName = attachment.file_name
        with open(attachmentFilePath, 'rb') as attachmentFile:
            response = FileResponse(attachmentFile, as_attachment=True, filename=attachmentFileName)
            return response


    URL_PATH_TOGGLE_FAVORITE = 'toggle-favorite'
    URL_NAME_TOGGLE_FAVORITE = 'toggle-favorite'
    @action(detail=True, methods=['post'], url_path=URL_PATH_TOGGLE_FAVORITE, url_name=URL_NAME_TOGGLE_FAVORITE)
    def toggle_favorite(self, request: Request, pk: int|None = None) -> Response:
        """Action method toggling the favorite flag of the attachment.

        Args:
            request: The request triggering the action.
            pk: The private key of the attachment to toggle favorite. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        attachment = self.get_object()
        attachment.is_favorite = not attachment.is_favorite
        attachment.save(update_fields=['is_favorite'])
        return Response({'detail': 'Attachment marked as favorite'})
