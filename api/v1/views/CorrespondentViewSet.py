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

from typing import TYPE_CHECKING, Final

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from api.v1.mixins.ToggleFavoriteMixin import ToggleFavoriteMixin
from core.models.CorrespondentModel import CorrespondentModel

from ..filters.CorrespondentFilter import CorrespondentFilter
from ..serializers.correspondent_serializers.BaseCorrespondentSerializer import (
    BaseCorrespondentSerializer,
)
from ..serializers.correspondent_serializers.CorrespondentSerializer import (
    CorrespondentSerializer,
)


if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.permissions import BasePermission
    from rest_framework.serializers import BaseSerializer


class CorrespondentViewSet(viewsets.ReadOnlyModelViewSet, ToggleFavoriteMixin):
    """Viewset for the :class:`core.models.CorrespondentModel.CorrespondentModel`."""

    BASENAME = CorrespondentModel.BASENAME
    serializer_class = CorrespondentSerializer
    filter_backends: Final[list] = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CorrespondentFilter
    permission_classes: Final[list[type[BasePermission]]] = [IsAuthenticated]
    ordering_fields: Final[list[str]] = [
        "email_name",
        "email_address",
        "is_favorite",
        "created",
        "updated",
    ]
    ordering: Final[list[str]] = ["id"]

    def get_queryset(self) -> QuerySet[CorrespondentModel]:
        """Filters the data for entries connected to the request user.

        Returns:
            The correspondent entries matching the request user.
        """
        if getattr(self, "swagger_fake_view", False):
            return CorrespondentModel.objects.none()
        return CorrespondentModel.objects.filter(
            emails__mailbox__account__user=self.request.user
        ).distinct()

    def get_serializer_class(self) -> type[BaseSerializer]:
        """Sets the serializer for `list` requests to the simplified version."""
        if self.action == "list":
            return BaseCorrespondentSerializer
        return super().get_serializer_class()
