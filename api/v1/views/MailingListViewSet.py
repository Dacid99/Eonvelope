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

from typing import TYPE_CHECKING, Final, override

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models.MailingListModel import MailingListModel

from ..filters.MailingListFilter import MailingListFilter
from ..serializers.mailinglist_serializers.MailingListSerializer import (
    MailingListSerializer,
)


if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.permissions import BasePermission
    from rest_framework.request import Request


class MailingListViewSet(viewsets.ReadOnlyModelViewSet, mixins.DestroyModelMixin):
    """Viewset for the :class:`core.models.MailingListModel.MailingListModel`.

    Provides every read-only and a destroy action.
    """

    BASENAME = "mailinglists"
    serializer_class = MailingListSerializer
    filter_backends: Final[list] = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MailingListFilter
    permission_classes: Final[list[type[BasePermission]]] = [IsAuthenticated]
    ordering_fields: Final[list[str]] = [
        "list_id",
        "list_owner",
        "list_subscribe",
        "list_unsubscribe",
        "list_post",
        "list_help",
        "list_archive",
        "is_favorite",
        "created",
        "updated",
    ]
    ordering: Final[list[str]] = ["id"]

    @override
    def get_queryset(self) -> QuerySet[MailingListModel]:
        """Filters the data for entries connected to the request user.

        Returns:
            The mailingslist entries matching the request user.
        """
        if getattr(self, "swagger_fake_view", False):
            return MailingListModel.objects.none()
        return MailingListModel.objects.filter(
            emails__mailbox__account__user=self.request.user
        ).distinct()

    URL_PATH_TOGGLE_FAVORITE = "toggle-favorite"
    URL_NAME_TOGGLE_FAVORITE = "toggle-favorite"

    @action(
        detail=True,
        methods=["post"],
        url_path=URL_PATH_TOGGLE_FAVORITE,
        url_name=URL_NAME_TOGGLE_FAVORITE,
    )
    def toggle_favorite(self, request: Request, pk: int | None = None) -> Response:
        """Action method toggling the favorite flag of the mailinglist.

        Args:
            request: The request triggering the action.
            pk: The private key of the mailinglist to toggle favorite. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        mailinglist = self.get_object()
        mailinglist.is_favorite = not mailinglist.is_favorite
        mailinglist.save(update_fields=["is_favorite"])
        return Response({"detail": "Mailinglist marked as favorite"})
