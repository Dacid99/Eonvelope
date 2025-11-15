# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
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

from django.http import FileResponse, Http404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.openapi import OpenApiParameter, OpenApiResponse, OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.utils import query_param_list_to_typed_list
from api.v1.filters import AttachmentFilterSet
from api.v1.mixins.ToggleFavoriteMixin import ToggleFavoriteMixin
from api.v1.serializers import BaseAttachmentSerializer
from core.models import Attachment


if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request


@extend_schema_view(
    list=extend_schema(description="Lists all instances matching the filter."),
    retrieve=extend_schema(description="Retrieves a single instance."),
    destroy=extend_schema(description="Deletes a single instance."),
    download=extend_schema(
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="headers: Content-Disposition=attachment",
            )
        },
        description="Downloads an attachment instances file.",
    ),
    download_batch=extend_schema(
        parameters=[
            OpenApiParameter(
                "id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                required=True,
                explode=True,
                many=True,
                description="Accepts both id=1,2,3 and id=1&id=2&id=3 notation",
            )
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="Headers: Content-Disposition=attachment",
            )
        },
        description="Downloads multiple zipped attachment files.",
    ),
    download_thumbnail=extend_schema(
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="Headers: Content-Disposition=inline, X-Frame-Options = 'SAMEORIGIN', Content-Security-Policy = 'frame-ancestors 'self''",
            )
        },
        description="Downloads a single attachments thumbnail.",
    ),
    share_to_paperless=extend_schema(
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.STR,
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.STR,
                description="If the request to the Paperless server fails. The reason is given as the response data.",
            ),
        },
        description="Sends the attachment file to Paperless.",
    ),
    share_to_immich=extend_schema(
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.JSON_PTR,
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.STR,
                description="If the request to the Paperless server fails. The reason is given as the response data.",
            ),
        },
        description="Sends the attachment file to Immich.",
    ),
)
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
        return Attachment.objects.filter(  # type: ignore[misc]  # user auth is checked by permissions, we also test for this
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
        try:
            response = FileResponse(
                attachment.open_file(),
                as_attachment=True,
                filename=attachment.file_name,
                content_type=attachment.content_type or None,
            )
        except FileNotFoundError:
            raise Http404(_("Attachment file not found")) from None
        return response

    URL_PATH_DOWNLOAD_BATCH = "download"
    URL_NAME_DOWNLOAD_BATCH = "download-batch"

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
            ValidationError: If id param is missing or in invalid format.

        Returns:
            A fileresponse containing the requested file.
        """
        requested_id_query_params = request.query_params.getlist("id", [])
        if not requested_id_query_params:
            raise ValidationError(
                {"id": _("Attachment ids are required.")},
            )
        try:
            requested_ids = query_param_list_to_typed_list(
                requested_id_query_params, int
            )
        except ValueError:
            raise ValidationError(
                {"id": _("Attachment ids given in invalid format.")},
            ) from None
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
            content_type="application/zip",
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
        try:
            response = FileResponse(
                attachment.open_file(),
                as_attachment=False,
                filename=attachment.file_name,
                content_type=attachment.content_type or None,
            )
        except FileNotFoundError:
            raise Http404(_("Attachment file not found")) from None
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response

    URL_PATH_SHARE_TO_PAPERLESS = "share/paperless"
    URL_NAME_SHARE_TO_PAPERLESS = "share-to-paperless"

    @action(
        detail=True,
        methods=["post"],
        url_path=URL_PATH_SHARE_TO_PAPERLESS,
        url_name=URL_NAME_SHARE_TO_PAPERLESS,
    )
    def share_to_paperless(self, request: Request, pk: int | None = None) -> Response:
        """Action method sending the attachment to the users Paperless server.

        Args:
            request: The request triggering the action.
            pk: The private key of the attachment to upload. Defaults to None.

        Raises:
            Http404: If the filepath is not in the database or it doesn't exist.

        Returns:
            A fileresponse containing the requested file.
        """
        attachment = self.get_object()
        try:
            paperless_response = attachment.share_to_paperless()
        except FileNotFoundError:
            raise Http404(_("Attachment file not found")) from None
        except (RuntimeError, ConnectionError, PermissionError, ValueError) as error:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                # Translators: Paperless is a brand name.
                data={"detail": _("Upload to Paperless failed."), "error": str(error)},
            )
        return Response(
            status=status.HTTP_200_OK,
            data={
                # Translators: Paperless is a brand name.
                "detail": _("Uploaded attachment document to Paperless."),
                "data": paperless_response,
            },
        )

    URL_PATH_SHARE_TO_IMMICH = "share/immich"
    URL_NAME_SHARE_TO_IMMICH = "share-to-immich"

    @action(
        detail=True,
        methods=["post"],
        url_path=URL_PATH_SHARE_TO_IMMICH,
        url_name=URL_NAME_SHARE_TO_IMMICH,
    )
    def share_to_immich(self, request: Request, pk: int | None = None) -> Response:
        """Action method sending the attachment to the users Immich server.

        Args:
            request: The request triggering the action.
            pk: The private key of the attachment to upload. Defaults to None.

        Raises:
            Http404: If the filepath is not in the database or it doesn't exist.

        Returns:
            A fileresponse containing the requested file.
        """
        attachment = self.get_object()
        try:
            immich_response = attachment.share_to_immich()
        except FileNotFoundError:
            raise Http404(_("Attachment file not found")) from None
        except (RuntimeError, ConnectionError, PermissionError, ValueError) as error:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                # Translators: Immich is a brand name.
                data={"detail": _("Upload to Immich failed."), "error": str(error)},
            )
        return Response(
            status=status.HTTP_200_OK,
            data={
                # Translators: Immich is a brand name.
                "detail": _("Uploaded attachment document to Immich."),
                "data": immich_response,
            },
        )
