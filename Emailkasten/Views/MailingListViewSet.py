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

"""Module with the :class:`MailingListViewSet` viewset."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..Filters.MailingListFilter import MailingListFilter
from ..Models.MailingListModel import MailingListModel
from ..Serializers.MailingListSerializers.MailingListSerializer import \
    MailingListSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request
    from django.db.models import BaseManager


class MailingListViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for the :class:`Emailkasten.Models.MailingListModel.MailingListModel`."""

    queryset = MailingListModel.objects.all()
    serializer_class = MailingListSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MailingListFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['list_id', 'list_owner', 'list_subscribe', 'list_unsubscribe', 'list_post', 'list_help', 'list_archive', 'correspondent__email_name', 'correspondent__email_address', 'created', 'updated']
    ordering = ['id']

    def get_queryset(self) -> BaseManager[MailingListModel]:
        """Filters the data for entries connected to the request user.

        Returns:
            The mailingslist entries matching the request user."""
        return MailingListModel.objects.filter(correspondent__emails__account__user = self.request.user).distinct()

    def destroy(self, request: Request, pk: int|None = None) -> Response:
        """Adds the `delete` action to the viewset."""
        try:
            instance = self.get_object()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except MailingListModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


    @action(detail=True, methods=['post'], url_path='toggle_favorite')
    def toggle_favorite(self, request: Request, pk: int|None = None) -> Response:
        """Action method toggling the favorite flag of the mailinglist.

        Args:
            request: The request triggering the action.
            pk: The private key of the mailinglist to toggle favorite. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        mailinglist = self.get_object()
        mailinglist.is_favorite = not mailinglist.is_favorite
        mailinglist.save(update_fields=['is_favorite'])
        return Response({'status': 'Mailinglist marked as favorite'})


    @action(detail=False, methods=['get'], url_path='favorites')
    def favorites(self, request: Request) -> Response:
        """Action method returning all mailinglist with favorite flag.

        Args:
            request: The request triggering the action.

        Returns:
            A response containing all mailinglist data with favorite flag.
        """
        favoriteMailinglists = MailingListModel.objects.filter(is_favorite=True)
        serializer = self.get_serializer(favoriteMailinglists, many=True)
        return Response(serializer.data)
