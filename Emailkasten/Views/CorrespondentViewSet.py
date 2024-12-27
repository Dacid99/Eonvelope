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

"""Module with the :class:`CorrespondentViewSet` viewset."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..Filters.CorrespondentFilter import CorrespondentFilter
from ..Models.CorrespondentModel import CorrespondentModel
from ..Serializers.CorrespondentSerializers.CorrespondentSerializer import \
    CorrespondentSerializer
from ..Serializers.CorrespondentSerializers.SimpleCorrespondentSerializer import \
    SimpleCorrespondentSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request
    from django.db.models import BaseManager


class CorrespondentViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for the :class:`Emailkasten.Models.CorrespondentModel.CorrespondentModel`."""

    BASENAME = 'correspondents'
    queryset = CorrespondentModel.objects.all()
    serializer_class = CorrespondentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CorrespondentFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['email_name', 'email_address', 'created']
    ordering = ['id']

    def get_queryset(self) -> BaseManager[CorrespondentModel]:
        """Filters the data for entries connected to the request user.

        Returns:
            The correspondent entries matching the request user."""
        return CorrespondentModel.objects.filter(emails__account__user = self.request.user).distinct()

    def get_serializer_class(self):
        """Sets the serializer for `list` requests to the simplified version."""
        if self.action == 'list':
            return SimpleCorrespondentSerializer
        return super().get_serializer_class()


    URL_PATH_TOGGLE_FAVORITE = 'toggle_favorite'
    URL_NAME_TOGGLE_FAVORITE = 'toggle-favorite'
    @action(detail=True, methods=['post'], url_path=URL_PATH_TOGGLE_FAVORITE, url_name=URL_NAME_TOGGLE_FAVORITE)
    def toggle_favorite(self, request: Request, pk: int|None = None) -> Response:
        """Action method toggling the favorite flag of the correspondent.

        Args:
            request: The request triggering the action.
            pk: The private key of the correspondent to toggle favorite. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        correspondent = self.get_object()
        correspondent.is_favorite = not correspondent.is_favorite
        correspondent.save(update_fields=['is_favorite'])
        return Response({'detail': 'Correspondent marked as favorite'})


    URL_PATH_FAVORITES = 'favorites'
    URL_NAME_FAVORITES = 'favorites'
    @action(detail=False, methods=['get'], url_path=URL_PATH_FAVORITES, url_name=URL_NAME_FAVORITES)
    def favorites(self, request: Request)-> Response:
        """Action method returning all correspondent with favorite flag.

        Args:
            request: The request triggering the action.

        Returns:
            A response containing all correspondents data with favorite flag.
        """
        favoriteCorrespondents = CorrespondentModel.objects.filter(is_favorite=True)
        serializer = self.get_serializer(favoriteCorrespondents, many=True)
        return Response(serializer.data)
