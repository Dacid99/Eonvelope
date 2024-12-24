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

from ..Filters.EMailFilter import EMailFilter
from ..Models.EMailModel import EMailModel
from ..Serializers.EMailSerializers.FullEMailSerializer import \
    FullEMailSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request
    from django.db.models import BaseManager


class EMailViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for the :class:`Emailkasten.Models.EMailModel.EMailModel`."""

    queryset = EMailModel.objects.all()
    serializer_class = FullEMailSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = EMailFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['datetime', 'email_subject', 'datasize', 'created', 'updated', 'user_agent', 'language', 'content_language', 'importance', 'priority', 'precedence', 'x_priority', 'x_originated_client']
    ordering = ['id']

    def get_queryset(self) -> BaseManager[EMailModel]:
        """Filters the data for entries connected to the request user.

        Returns:
            The email entries matching the request user."""
        return EMailModel.objects.filter(account__user = self.request.user)


    @action(detail=True, methods=['get'], url_path='download')
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


    @action(detail=True, methods=['get'], url_path='prerender')
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


    @action(detail=True, methods=['post'], url_path='toggle_favorite')
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
        return Response({'status': 'Email marked as favorite'})


    @action(detail=False, methods=['get'], url_path='favorites')
    def favorites(self, request: Request) -> Response:
        """Action method returning all emails with favorite flag.

        Args:
            request: The request triggering the action.

        Returns:
            A response containing all email data with favorite flag.
        """
        favoriteEmails = EMailModel.objects.filter(is_favorite=True)
        serializer = self.get_serializer(favoriteEmails, many=True)
        return Response(serializer.data)
