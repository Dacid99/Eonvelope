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

"""Module with the :class:`ImageViewSet` viewset."""

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

from ..Filters.ImageFilter import ImageFilter
from ..Models.ImageModel import ImageModel
from ..Serializers.ImageSerializers.ImageSerializer import ImageSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request
    from django.db.models import BaseManager


class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for the :class:`Emailkasten.Models.ImageModel.ImageModel`."""

    queryset = ImageModel.objects.all()
    serializer_class = ImageSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ImageFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['file_name', 'datasize', 'email__datetime', 'created', 'updated']
    ordering = ['id']

    def get_queryset(self) -> BaseManager[ImageModel]:
        """Filters the data for entries connected to the request user.

        Returns:
            The image entries matching the request user."""
        return ImageModel.objects.filter(email__account__user = self.request.user)


    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request: Request, pk: int|None = None) -> FileResponse:
        """Action method downloading the image.

        Args:
            request: The request triggering the action.
            pk: The private key of the image to download. Defaults to None.

        Raises:
            Http404: If the filepath is not in the database or it doesnt exist.

        Returns:
            A fileresponse containing the requested file.
        """
        image = self.get_object()

        imageFilePath = image.file_path
        if not imageFilePath or not os.path.exists(imageFilePath):
            raise Http404("Image file not found")

        imageFileName = image.file_name
        with open(imageFilePath, 'rb') as imageFile:
            response = FileResponse(imageFile, as_attachment=True, filename=imageFileName)
            return response


    @action(detail=True, methods=['post'], url_path='toggle_favorite')
    def toggle_favorite(self, request: Request, pk: int|None = None) -> Response:
        """Action method toggling the favorite flag of the image.

        Args:
            request: The request triggering the action.
            pk: The private key of the image to toggle favorite. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        image = self.get_object()
        image.is_favorite = not image.is_favorite
        image.save(update_fields=['is_favorite'])
        return Response({'status': 'Image marked as favorite'})


    @action(detail=False, methods=['get'], url_path='favorites')
    def favorites(self, request: Request) -> Response:
        """Action method returning all image with favorite flag.

        Args:
            request: The request triggering the action.

        Returns:
            A response containing all image data with favorite flag.
        """
        favoriteImages = ImageModel.objects.filter(is_favorite=True)
        serializer = self.get_serializer(favoriteImages, many=True)
        return Response(serializer.data)
