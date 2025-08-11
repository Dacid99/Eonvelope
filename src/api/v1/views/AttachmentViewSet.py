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

from typing import TYPE_CHECKING, Final, override

from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.openapi import OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
    """Viewset for the :class:`core.models.Attachment`.

    Provides every read-only and a destroy action.
    """

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
        return Attachment.objects.filter(  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
            email__mailbox__account__user=self.request.user
        ).select_related(
            "email"
        )

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
            Http404: If the filepath is not in the database or it doesn't exist.

        Returns:
            A fileresponse containing the requested file.
        """
        attachment = self.get_object()

        attachment_file_path = attachment.file_path
        if not attachment_file_path or not default_storage.exists(attachment_file_path):
            raise Http404(_("Attachment file not found"))

        attachment_file_name = attachment.file_name
        return FileResponse(
            default_storage.open(attachment_file_path, "rb"),
            as_attachment=True,
            filename=attachment_file_name,
        )

    URL_PATH_DOWNLOAD_BATCH = "download"
    URL_NAME_DOWNLOAD_BATCH = "download-batch"

    @extend_schema(
        parameters=[OpenApiParameter("id", OpenApiTypes.INT, OpenApiParameter.QUERY)]
    )
    @action(
        detail=False,
        methods=["get"],
        url_path=URL_PATH_DOWNLOAD_BATCH,
        url_name=URL_NAME_DOWNLOAD_BATCH,
    )
    def download_batch(self, request: Request) -> Response | FileResponse:
        """Action method downloading a batch of attachments.

        Args:
            request: The request triggering the action.

        Raises:
            Http404: If no downloadable attachment has been requested.

        Returns:
            A fileresponse containing the requested file.
            A 400 response if the id param is missing in the request.
        """
        requested_ids = request.query_params.getlist("id", [])
        if not requested_ids:
            return Response(
                {"detail": _("Attachment ids missing in request.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            file = Attachment.queryset_as_file(
                self.get_queryset().filter(pk__in=requested_ids)
            )
        except Attachment.DoesNotExist:
            raise Http404(_("No attachments found")) from None
        return FileResponse(
            file,
            as_attachment=True,
            filename="attachments.zip",
        )

    URL_PATH_THUMBNAIL = "thumbnail"
    URL_NAME_THUMBNAIL = "thumbnail"

    @action(
        detail=True,
        methods=["get"],
        url_path=URL_PATH_THUMBNAIL,
        url_name=URL_NAME_THUMBNAIL,
    )
    def download_thumbnail(
        self, request: Request, pk: int | None = None
    ) -> FileResponse:
        """Action method downloading the attachment thumbnail.

        Returns the same filedata as 'download', but as inline.

        Args:
            request: The request triggering the action.
            pk: The private key of the attachment to download. Defaults to None.

        Raises:
            Http404: If the filepath is not in the database or it doesn't exist.

        Returns:
            A fileresponse containing the requested file.
        """
        attachment = self.get_object()

        attachment_file_path = attachment.file_path
        if not attachment_file_path or not default_storage.exists(attachment_file_path):
            raise Http404(_("Attachment file not found"))

        attachment_file_name = attachment.file_name
        response = FileResponse(
            default_storage.open(attachment_file_path, "rb"),
            as_attachment=False,
            filename=attachment_file_name,
            content_type=attachment.content_type,
        )
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response
