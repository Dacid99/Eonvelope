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

"""Module with the :class:`MailboxViewSet` viewset."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core import constants
from core.constants import TestStatusCodes
from core.models.DaemonModel import DaemonModel
from core.models.EMailModel import EMailModel
from core.models.MailboxModel import MailboxModel

from ..filters.MailboxFilter import MailboxFilter
from ..serializers.mailbox_serializers.MailboxWithDaemonSerializer import (
    MailboxWithDaemonSerializer,
)

if TYPE_CHECKING:
    from django.db.models import BaseManager
    from rest_framework.request import Request


class MailboxViewSet(viewsets.ModelViewSet):
    """Viewset for the :class:`core.models.MailboxModel.MailboxModel`."""

    BASENAME = "mailboxes"
    serializer_class = MailboxWithDaemonSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MailboxFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = [
        "name",
        "account__mail_address",
        "account__mail_host",
        "account__protocol",
        "save_attachments",
        "save_toEML",
        "is_favorite",
        "is_healthy",
        "created",
        "updated",
    ]
    ordering = ["id"]

    def get_queryset(self) -> BaseManager[MailboxModel]:
        """Filters the data for entries connected to the request user.

        Returns:
            The mailbox entries matching the request user."""
        return MailboxModel.objects.filter(account__user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Disables the POST method for this viewset."""
        return Response(
            {"detail": "POST method is not allowed on this endpoint."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    URL_PATH_ADD_DAEMON = "add-daemon"
    URL_NAME_ADD_DAEMON = "add-daemon"

    @action(
        detail=True,
        methods=["POST"],
        url_path=URL_PATH_ADD_DAEMON,
        url_name=URL_NAME_ADD_DAEMON,
    )
    def add_daemon(self, request: Request, pk: int | None = None) -> Response:
        """Action method creating a new daemon for the mailbox.

        Args:
            request: The request triggering the action.
            pk: The private key of the mailbox. Defaults to None.

        Returns:
            A response containing the updated mailbox data.
        """
        mailbox = self.get_object()
        DaemonModel.objects.create(mailbox=mailbox)

        mailboxSerializer = self.get_serializer(mailbox)
        return Response(
            {"detail": "Added daemon for mailbox", "mailbox": mailboxSerializer.data}
        )

    URL_PATH_TEST = "test"
    URL_NAME_TEST = "test"

    @action(
        detail=True, methods=["post"], url_path=URL_PATH_TEST, url_name=URL_NAME_TEST
    )
    def test_mailbox(self, request: Request, pk: int | None = None) -> Response:
        """Action method testing the mailbox data.

        Args:
            request: The request triggering the action.
            pk: The private key of the mailbox to test. Defaults to None.

        Returns:
            A response containing the updated mailbox data and the test resultcode.
        """
        mailbox = self.get_object()
        result = mailbox.test_connection()

        mailboxSerializer = self.get_serializer(mailbox)
        return Response(
            {
                "detail": "Tested mailbox",
                "mailbox": mailboxSerializer.data,
                "result": TestStatusCodes.INFOS[result],
            }
        )

    URL_PATH_FETCH_ALL = "fetch-all"
    URL_NAME_FETCH_ALL = "fetch-all"

    @action(
        detail=True,
        methods=["post"],
        url_path=URL_PATH_FETCH_ALL,
        url_name=URL_NAME_FETCH_ALL,
    )
    def fetch_all(self, request: Request, pk: int | None = None) -> Response:
        """Action method fetching all mails from the mailbox.

        Args:
            request: The request triggering the action.
            pk: The private key of the mailbox. Defaults to None.

        Returns:
            A response with the mailbox data.
        """
        mailbox = self.get_object()
        mailbox.fetch(constants.MailFetchingCriteria.ALL)
        mailboxSerializer = self.get_serializer(mailbox)
        return Response(
            {"detail": "All mails fetched", "mailbox": mailboxSerializer.data}
        )

    URL_PATH_UPLOAD_EML = "upload-eml"
    URL_NAME_UPLOAD_EML = "upload-eml"

    @action(
        detail=True,
        methods=["post"],
        url_path=URL_PATH_UPLOAD_EML,
        url_name=URL_NAME_UPLOAD_EML,
    )
    def upload_eml(self, request: Request, pk: int | None = None) -> Response:
        """Action method toggling the favorite flag of the mailbox.

        Args:
            request: The request triggering the action.
            pk: int: The private key of the mailbox to upload to. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        uploaded_mbox_file = request.FILES.get("eml", None)
        if uploaded_mbox_file is None:
            return Response(
                {"detail": "EML file missing in request!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        mailbox = self.get_object()
        EMailModel.createFromEmailBytes(uploaded_mbox_file.read(), mailbox)
        mailboxSerializer = self.get_serializer(mailbox)
        return Response(
            {
                "detail": "Successfully uploaded mbox file",
                "mailbox": mailboxSerializer.data,
            }
        )

    URL_PATH_UPLOAD_MBOX = "upload-mbox"
    URL_NAME_UPLOAD_MBOX = "upload-mbox"

    @action(
        detail=True,
        methods=["post"],
        url_path=URL_PATH_UPLOAD_MBOX,
        url_name=URL_NAME_UPLOAD_MBOX,
    )
    def upload_mbox(self, request: Request, pk: int | None = None) -> Response:
        """Action method toggling the favorite flag of the mailbox.

        Args:
            request: The request triggering the action.
            pk: int: The private key of the mailbox to upload to. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        uploaded_mbox_file = request.FILES.get("mbox", None)
        if uploaded_mbox_file is None:
            return Response(
                {"detail": "MBOX file missing in request!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        mailbox = self.get_object()
        mailbox.addFromMBOX(uploaded_mbox_file.read())
        mailboxSerializer = self.get_serializer(mailbox)
        return Response(
            {
                "detail": "Successfully uploaded mbox file",
                "mailbox": mailboxSerializer.data,
            }
        )

    URL_PATH_TOGGLE_FAVORITE = "toggle-favorite"
    URL_NAME_TOGGLE_FAVORITE = "toggle-favorite"

    @action(
        detail=True,
        methods=["post"],
        url_path=URL_PATH_TOGGLE_FAVORITE,
        url_name=URL_NAME_TOGGLE_FAVORITE,
    )
    def toggle_favorite(self, request: Request, pk: int | None = None) -> Response:
        """Action method toggling the favorite flag of the mailbox.

        Args:
            request: The request triggering the action.
            pk: int: The private key of the mailbox to toggle favorite. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        mailbox = self.get_object()
        mailbox.is_favorite = not mailbox.is_favorite
        mailbox.save(update_fields=["is_favorite"])
        return Response({"detail": "Mailbox marked as favorite"})
