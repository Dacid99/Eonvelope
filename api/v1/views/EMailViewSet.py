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

"""Module with the :class:`EMailViewSet` viewset."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Final

from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.mixins.ToggleFavoriteMixin import ToggleFavoriteMixin
from core.models.EMailModel import EMailModel

from ..filters.EMailFilter import EMailFilter
from ..serializers.email_serializers.EMailSerializer import EMailSerializer
from ..serializers.email_serializers.FullEMailSerializer import FullEMailSerializer


if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.permissions import BasePermission
    from rest_framework.request import Request


class EMailViewSet(viewsets.ReadOnlyModelViewSet, ToggleFavoriteMixin):
    """Viewset for the :class:`core.models.EMailModel.EMailModel`."""

    BASENAME = EMailModel.BASENAME
    serializer_class = FullEMailSerializer
    filter_backends: Final[list] = [DjangoFilterBackend, OrderingFilter]
    filterset_class = EMailFilter
    permission_classes: Final[list[type[BasePermission]]] = [IsAuthenticated]
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

    def get_queryset(self) -> QuerySet[EMailModel]:
        """Filters the data for entries connected to the request user.

        Returns:
            The email entries matching the request user.
        """
        if getattr(self, "swagger_fake_view", False):
            return EMailModel.objects.none()
        return EMailModel.objects.filter(mailbox__account__user=self.request.user)

    def destroy(self, request: Request, pk: int | None = None) -> Response:
        """Adds the `delete` action to the viewset."""
        try:
            instance = self.get_object()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except EMailModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

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

        filePath = email.eml_filepath
        if not filePath or not os.path.exists(filePath):
            raise Http404("EMl file not found")

        fileName = os.path.basename(filePath)
        return FileResponse(open(filePath, "rb"), as_attachment=True, filename=fileName)

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

        htmlFilePath = email.html_filepath
        if not htmlFilePath or not os.path.exists(htmlFilePath):
            raise Http404("Html file not found")

        htmlFileName = os.path.basename(htmlFilePath)
        response = FileResponse(
            open(  # noqa: SIM115 ;  this is the recommended usage for FileResponse, see https://docs.djangoproject.com/en/5.2/ref/request-response/
                htmlFilePath, "rb"
            ),
            as_attachment=False,
            filename=htmlFileName,
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
    def fullConversation(self, request: Request, pk: int | None = None) -> Response:
        """Action method getting the complete conversation a mail is part of.

        Args:
            request: The request triggering the action.
            pk: The private key of the email to get the complete conversation it belongs to. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        email = self.get_object()
        conversation = email.fullConversation()
        conversationSerializer = EMailSerializer(conversation, many=True)
        return Response({"emails": conversationSerializer.data})

    URL_PATH_SUBCONVERSATION = "sub-conversation"
    URL_NAME_SUBCONVERSATION = "sub-conversation"

    @action(
        detail=True,
        methods=["get"],
        url_path=URL_PATH_SUBCONVERSATION,
        url_name=URL_NAME_SUBCONVERSATION,
    )
    def subConversation(self, request: Request, pk: int | None = None) -> Response:
        """Action method getting the subconversation in reply to this email.

        Args:
            request: The request triggering the action.
            pk: The private key of the email to get the subconversation in its wake. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        email = self.get_object()
        conversation = email.subConversation()
        conversationSerializer = EMailSerializer(conversation, many=True)
        return Response({"emails": conversationSerializer.data})
