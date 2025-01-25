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

"""Module with the :class:`EMailViewSet` viewset."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Emailkasten.Filters.EMailFilter import EMailFilter
from core.models.EMailModel import EMailModel
from Emailkasten.Serializers.EMailSerializers.FullEMailSerializer import \
    FullEMailSerializer

if TYPE_CHECKING:
    from django.db.models import BaseManager
    from rest_framework.request import Request


class EMailViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for the :class:`core.models.EMailModel.EMailModel`."""

    BASENAME = 'emails'
    serializer_class = FullEMailSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = EMailFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['datetime', 'email_subject', 'datasize', 'is_favorite','created', 'updated', 'user_agent', 'language', 'content_language', 'importance', 'priority', 'precedence', 'x_priority', 'x_originated_client']
    ordering = ['id']

    def get_queryset(self) -> BaseManager[EMailModel]:
        """Filters the data for entries connected to the request user.

        Returns:
            The email entries matching the request user."""
        return EMailModel.objects.filter(account__user = self.request.user)


    def destroy(self, request: Request, pk: int|None = None) -> Response:
        """Adds the `delete` action to the viewset."""
        try:
            instance = self.get_object()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except EMailModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


    URL_PATH_DOWNLOAD = 'download'
    URL_NAME_DOWNLOAD = 'download'
    @action(detail=True, methods=['get'], url_path=URL_PATH_DOWNLOAD, url_name=URL_NAME_DOWNLOAD)
    def download(self, request: Request, pk: int|None = None) -> FileResponse:
        """Action method downloading the eml file of the email.

        Args:
            request: The request triggering the action.
            pk: int: The private key of the attachment to download. Defaults to None.

        Raises:
            Http404: If the filepath is not in the database or it doesnt exist.

        Returns:
            A fileresponse containing the requested file.
        """
        email = self.get_object()

        filePath = email.eml_filepath
        if not filePath or not os.path.exists(filePath):
            raise Http404("EMl file not found")

        fileName = os.path.basename(filePath)
        with open(filePath, 'rb') as file:
            response = FileResponse(file, as_attachment=True, filename=fileName)
            return response


    URL_PATH_PRERENDER = 'prerender'
    URL_NAME_PRERENDER = 'prerender'
    @action(detail=True, methods=['get'], url_path=URL_PATH_PRERENDER, url_name=URL_NAME_PRERENDER)
    def prerender(self, request: Request, pk: int|None = None) -> FileResponse:
        """Action method downloading the prerender image of the mail.

        Args:
            request: The request triggering the action.
            pk: int: The private key of the attachment to download. Defaults to None.

        Raises:
            Http404: If the filepath is not in the database or it doesnt exist.

        Returns:
            A fileresponse containing the requested file.
        """
        email = self.get_object()

        prerenderFilePath = email.prerender_filepath
        if not prerenderFilePath or not os.path.exists(prerenderFilePath):
            raise Http404("Prerender image file not found")

        prerenderFileName = os.path.basename(prerenderFilePath)
        with open(prerenderFilePath, 'rb') as prerenderFile:
            response = FileResponse(prerenderFile, as_attachment=True, filename=prerenderFileName)
            return response


    URL_PATH_TOGGLE_FAVORITE = 'toggle_favorite'
    URL_NAME_TOGGLE_FAVORITE = 'toggle-favorite'
    @action(detail=True, methods=['post'], url_path=URL_PATH_TOGGLE_FAVORITE, url_name=URL_NAME_TOGGLE_FAVORITE)
    def toggle_favorite(self, request: Request, pk: int|None = None) -> Response:
        """Action method toggling the favorite flag of the email.

        Args:
            request: The request triggering the action.
            pk: int: The private key of the email to toggle favorite. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        email = self.get_object()
        email.is_favorite = not email.is_favorite
        email.save(update_fields=['is_favorite'])
        return Response({'detail': 'Email marked as favorite'})
