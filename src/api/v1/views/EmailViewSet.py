# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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

"""Module with the :class:`EmailViewSet` viewset."""

from __future__ import annotations

import os
from io import BytesIO
from typing import TYPE_CHECKING, Final, override

from django.core.files.storage import default_storage
from django.db.models import Prefetch
from django.http import FileResponse, Http404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.openapi import OpenApiParameter, OpenApiResponse, OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.utils import query_param_list_to_typed_list
from api.v1.filters import EmailFilterSet
from api.v1.mixins.ToggleFavoriteMixin import ToggleFavoriteMixin
from api.v1.serializers import BaseEmailSerializer, FullEmailSerializer
from core.constants import SupportedEmailDownloadFormats
from core.models import Email, EmailCorrespondent


if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request
    from rest_framework.serializers import BaseSerializer


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
        description="Downloads the email instances eml file.",
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
            ),
            OpenApiParameter(
                "file_format",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                enum=SupportedEmailDownloadFormats,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="Headers: Content-Disposition=attachment",
            )
        },
        description="Downloads multiple emails.",
    ),
    download_thumbnail=extend_schema(
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="Headers: Content-Disposition=inline, X-Frame-Options = 'SAMEORIGIN', Content-Security-Policy = 'frame-ancestors 'self''",
            )
        },
        description="Downloads a single emails thumbnail.",
    ),
    conversation=extend_schema(
        responses=BaseEmailSerializer(many=True),
        description="Lists the conversation involving the email instance.",
    ),
)
class EmailViewSet(
    viewsets.ReadOnlyModelViewSet[Email],
    mixins.DestroyModelMixin,
    ToggleFavoriteMixin,
):
    """Viewset for the :class:`core.models.Email.Email`.

    Provides every read-only and a destroy action.
    """

    BASENAME = Email.BASENAME
    serializer_class = FullEmailSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = EmailFilterSet
    permission_classes = [IsAuthenticated]
    ordering_fields: Final[list[str]] = [
        "datetime",
        "subject",
        "datasize",
        "is_favorite",
        "created",
        "updated",
        "user_agent",
        "language",
        "content_language",
        "importance",
        "priority",
        "precedence",
        "x_priority",
        "x_originated_client",
    ]
    ordering: Final[list[str]] = ["id"]

    @override
    def get_queryset(self) -> QuerySet[Email]:
        """Filters the data for entries connected to the request user.

        Returns:
            The email entries matching the request user.
        """
        if getattr(self, "swagger_fake_view", False):
            return Email.objects.none()
        return (
            Email.objects.filter(mailbox__account__user=self.request.user)  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
            .prefetch_related(
                "attachments", "in_reply_to", "replies", "references", "referenced_by"
            )
            .prefetch_related(
                Prefetch(
                    "emailcorrespondents",
                    queryset=EmailCorrespondent.objects.select_related("correspondent"),
                )
            )
        )

    @override
    def get_serializer_class(self) -> type[BaseSerializer[Email]]:
        """Sets the serializer for `list` requests to the simplified version."""
        if self.action == "list":
            return BaseEmailSerializer
        return super().get_serializer_class()

    URL_PATH_DOWNLOAD = "download"
    URL_NAME_DOWNLOAD = "download"

    @action(
        detail=True,
        methods=["get"],
        url_path=URL_PATH_DOWNLOAD,
        url_name=URL_NAME_DOWNLOAD,
    )
    def download(self, request: Request, pk: int | None = None) -> FileResponse:
        """Action method downloading the eml file of the email.

        Args:
            request: The request triggering the action.
            pk: The private key of the attachment to download. Defaults to None.

        Raises:
            Http404: If the filepath is not in the database or it doesn't exist.

        Returns:
            A fileresponse containing the requested file.
        """
        email = self.get_object()

        file_path = email.eml_filepath
        if not file_path or not default_storage.exists(file_path):
            raise Http404(_("eml file not found"))

        file_name = os.path.basename(file_path)
        return FileResponse(
            default_storage.open(file_path, "rb"),
            as_attachment=True,
            filename=file_name,
            content_type="message/rfc822",
        )

    URL_PATH_DOWNLOAD_BATCH = "download"
    URL_NAME_DOWNLOAD_BATCH = "download-batch"

    @action(
        detail=False,
        methods=["get"],
        url_path=URL_PATH_DOWNLOAD_BATCH,
        url_name=URL_NAME_DOWNLOAD_BATCH,
    )
    def download_batch(self, request: Request) -> Response | FileResponse:
        """Action method downloading a batch of emails.

        Todo:
            Validation and parsing of queryparams can probably be done more concisely with a serializer.

        Args:
            request: The request triggering the action.

        Raises:
            Http404: If there are no emails in the mailbox.
            ValidationError: If id or file_format param is missing or in invalid format or file_format is unsupported.

        Returns:
            A fileresponse containing the emails in the requested format.
        """
        file_format = request.query_params.get("file_format", None)
        if not file_format:
            raise ValidationError(
                {"file_format": _("File format is required.")},
            )
        requested_id_query_params = request.query_params.getlist("id", [])
        if not requested_id_query_params:
            raise ValidationError(
                {"id": _("Email ids are required.")},
            )
        try:
            requested_ids = query_param_list_to_typed_list(
                requested_id_query_params, int
            )
        except ValueError:
            raise ValidationError(
                {"id": _("Email ids given in invalid format.")},
            ) from None
        try:
            file = Email.queryset_as_file(
                self.get_queryset().filter(pk__in=requested_ids), file_format
            )
        except ValueError:
            raise ValidationError(
                {
                    "file_format": _("File format %(file_format)s is not supported.")
                    % {"file_format": file_format}
                },
            ) from None
        except Email.DoesNotExist:
            raise Http404(_("No emails found")) from None
        return FileResponse(
            file,
            as_attachment=True,
            filename=f"emails.{file_format.split('[', maxsplit=1)[0]}",
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
        """Action method downloading the html version of the mail.

        Args:
            request: The request triggering the action.
            pk: The private key of the email to download. Defaults to None.

        Returns:
            A fileresponse containing the requested file.
        """
        email = self.get_object()

        response = FileResponse(
            BytesIO(email.html_version.encode()),
            as_attachment=False,
            filename=email.message_id + ".html",
            content_type="text/html",
        )
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response

    URL_PATH_FULLCONVERSATION = "full-conversation"
    URL_NAME_FULLCONVERSATION = "full-conversation"

    @action(
        detail=True,
        methods=["get"],
        url_path=URL_PATH_FULLCONVERSATION,
        url_name=URL_NAME_FULLCONVERSATION,
    )
    def conversation(self, request: Request, pk: int | None = None) -> Response:
        """Action method getting the complete conversation a mail is part of.

        The response data is paginated analogous to the list method.

        Args:
            request: The request triggering the action.
            pk: The private key of the email to get the complete conversation it belongs to. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        email = self.get_object()
        conversation = email.conversation

        page = self.paginate_queryset(conversation)
        if page is not None:
            conversation_serializer = BaseEmailSerializer(page, many=True)
            return self.get_paginated_response(conversation_serializer.data)

        conversation_serializer = BaseEmailSerializer(conversation, many=True)
        return Response(conversation_serializer.data)
