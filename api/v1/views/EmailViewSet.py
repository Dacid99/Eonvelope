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

"""Module with the :class:`EmailViewSet` viewset."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Final, override

from django.core.files.storage import default_storage
from django.db.models import Prefetch
from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.mixins.ToggleFavoriteMixin import ToggleFavoriteMixin
from core.models import Email, EmailCorrespondent

from ..filters import EmailFilterSet
from ..serializers import EmailSerializer, FullEmailSerializer


if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request


class EmailViewSet(
    viewsets.ReadOnlyModelViewSet[Email],
    mixins.DestroyModelMixin,
    ToggleFavoriteMixin,
):
    """Viewset for the :class:`core.models.Email.Email`.
    `core.models.Email`
        Provides every read-only and a destroy action.
    """

    BASENAME = Email.BASENAME
    serializer_class = FullEmailSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = EmailFilterSet
    permission_classes = [IsAuthenticated]
    ordering_fields: Final[list[str]] = [
        "datetime",
        "email_subject",
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
        if not self.request.user.is_authenticated:
            return Email.objects.none()
        return (
            Email.objects.filter(mailbox__account__user=self.request.user)
            .select_related("mailinglist", "in_reply_to")
            .prefetch_related("attachments", "references", "referenced_by")
            .prefetch_related(
                Prefetch(
                    "emailcorrespondents",
                    queryset=EmailCorrespondent.objects.select_related("correspondent"),
                )
            )
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
        """Action method downloading the eml file of the email.

        Args:
            request: The request triggering the action.
            pk: The private key of the attachment to download. Defaults to None.

        Raises:
            Http404: If the filepath is not in the database or it doesnt exist.

        Returns:
            A fileresponse containing the requested file.
        """
        email = self.get_object()

        file_path = email.eml_filepath
        if not file_path or not os.path.exists(file_path):
            raise Http404("EMl file not found")

        file_name = os.path.basename(file_path)
        return FileResponse(
            default_storage.open(file_path, "rb"),
            as_attachment=True,
            filename=file_name,
        )

    URL_PATH_DOWNLOAD_BATCH = "download"
    URL_NAME_DOWNLOAD_BATCH = "download-batch"

    @action(
        detail=False,
        methods=["get"],
        url_path=URL_PATH_DOWNLOAD_BATCH,
        url_name=URL_NAME_DOWNLOAD_BATCH,
    )
    def download_batch(self, request: Request) -> FileResponse:
        """Action method downloading a batch of emails.

        Args:
            request: The request triggering the action.

        Returns:
            A fileresponse containing the emails in the requested format.
            A 400 response if file_format or id param are missing in the request.
            A 404 response if the queryset is empty.
        """
        file_format = request.query_params.get("file_format", None)
        if not file_format:
            return Response(
                {"detail": "File format missing in request!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        requested_ids = request.query_params.getlist("id", [])
        if not requested_ids:
            return Response(
                {"detail": "Email ids missing in request!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            file = Email.queryset_as_file(
                self.get_queryset().filter(pk__in=requested_ids), file_format
            )
        except ValueError:
            return Response(
                {"detail": f"File format {file_format} is not supported!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Email.DoesNotExist:
            raise Http404("No emails found") from None
        else:
            return FileResponse(
                file,
                as_attachment=True,
                filename=f"emails.{file_format.split("[", maxsplit=1)[0]}",
            )

    URL_PATH_DOWNLOAD_HTML = "download-html"
    URL_NAME_DOWNLOAD_HTML = "download-html"

    @action(
        detail=True,
        methods=["get"],
        url_path=URL_PATH_DOWNLOAD_HTML,
        url_name=URL_NAME_DOWNLOAD_HTML,
    )
    def download_html(self, request: Request, pk: int | None = None) -> FileResponse:
        """Action method downloading the html version of the mail.

        Args:
            request: The request triggering the action.
            pk: The private key of the email to download. Defaults to None.

        Raises:
            Http404: If the filepath is not in the database or it doesnt exist.

        Returns:
            A fileresponse containing the requested file.
        """
        email = self.get_object()

        html_file_path = email.html_filepath
        if not html_file_path or not os.path.exists(html_file_path):
            raise Http404("Html file not found")

        html_file_name = os.path.basename(html_file_path)
        response = FileResponse(
            default_storage.open(html_file_path, "rb"),
            as_attachment=False,
            filename=html_file_name,
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
    def full_conversation(self, request: Request, pk: int | None = None) -> Response:
        """Action method getting the complete conversation a mail is part of.

        Args:
            request: The request triggering the action.
            pk: The private key of the email to get the complete conversation it belongs to. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        email = self.get_object()
        conversation = email.full_conversation()
        conversation_serializer = EmailSerializer(conversation, many=True)
        return Response({"emails": conversation_serializer.data})

    URL_PATH_SUBCONVERSATION = "sub-conversation"
    URL_NAME_SUBCONVERSATION = "sub-conversation"

    @action(
        detail=True,
        methods=["get"],
        url_path=URL_PATH_SUBCONVERSATION,
        url_name=URL_NAME_SUBCONVERSATION,
    )
    def sub_conversation(self, request: Request, pk: int | None = None) -> Response:
        """Action method getting the subconversation in reply to this email.

        Args:
            request: The request triggering the action.
            pk: The private key of the email to get the subconversation in its wake. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        email = self.get_object()
        conversation = email.sub_conversation()
        conversation_serializer = EmailSerializer(conversation, many=True)
        return Response({"emails": conversation_serializer.data})
