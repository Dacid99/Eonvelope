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
from typing import TYPE_CHECKING, Final, override

from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from api.v1.mixins.ToggleFavoriteMixin import ToggleFavoriteMixin
from core.models import Attachment

from ..filters import AttachmentFilterSet
from ..serializers import BaseAttachmentSerializer


if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request


class AttachmentViewSet(
    viewsets.ReadOnlyModelViewSet[Attachment],
    mixins.DestroyModelMixin,
    ToggleFavoriteMixin,
):
    """Viewset for the :class:`core.models.Attachment`."""

    BASENAME = Attachment.BASENAME
    serializer_class = BaseAttachmentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AttachmentFilterSet
    permission_classes = [IsAuthenticated]
    ordering_fields: Final[list[str]] = [
        "file_name",
        "datasize",
        "email__datetime",
        "is_favorite",
        "created",
        "updated",
    ]
    ordering: Final[list[str]] = ["id"]

    @override
    def get_queryset(self) -> QuerySet[Attachment]:
        """Filters the data for entries connected to the request user.

        Returns:
            The attachment entries matching the request user.
        """
        if getattr(self, "swagger_fake_view", False):
            return Attachment.objects.none()
        if not self.request.user.is_authenticated:
            return Attachment.objects.none()
        return Attachment.objects.filter(
            email__mailbox__account__user=self.request.user
        ).select_related("email")

    URL_PATH_DOWNLOAD = "download"
    URL_NAME_DOWNLOAD = "download"

    @action(
        detail=True,
        methods=["get"],
        url_path=URL_PATH_DOWNLOAD,
        url_name=URL_NAME_DOWNLOAD,
    )
    def download(self, request: Request, pk: int | None = None) -> FileResponse:
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

        attachment_file_path = attachment.file_path
        if not attachment_file_path or not os.path.exists(attachment_file_path):
            raise Http404("Attachment file not found")

        attachment_file_name = attachment.file_name
        return FileResponse(
            open(attachment_file_path, "rb"),
            as_attachment=True,
            filename=attachment_file_name,
        )
