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
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from api.v1.mixins.ToggleFavoriteMixin import ToggleFavoriteMixin
from core.models.MailingList import MailingList

from ..filters.MailingListFilterSet import MailingListFilterSet
from ..serializers.mailinglist_serializers.MailingListSerializer import (
    MailingListSerializer,
)


if TYPE_CHECKING:
    from django.db.models import QuerySet


class MailingListViewSet(
    viewsets.ReadOnlyModelViewSet[MailingList],
    mixins.DestroyModelMixin,
    ToggleFavoriteMixin,
):
    """Viewset for the :class:`core.models.MailingList.MailingList`.

    Provides every read-only and a destroy action.
    """

    BASENAME = MailingList.BASENAME
    serializer_class = MailingListSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MailingListFilterSet
    permission_classes = [IsAuthenticated]
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
    def get_queryset(self) -> QuerySet[MailingList]:
        """Filters the data for entries connected to the request user.

        Returns:
            The mailingslist entries matching the request user.
        """
        if getattr(self, "swagger_fake_view", False):
            return MailingList.objects.none()
        if not self.request.user.is_authenticated:
            return MailingList.objects.none()
        return (
            MailingList.objects.filter(emails__mailbox__account__user=self.request.user)
            .distinct()
            .prefetch_related("emails")
        )
