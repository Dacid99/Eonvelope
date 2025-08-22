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

from typing import TYPE_CHECKING, Final, override

from django.http import FileResponse, Http404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.mixins.ToggleFavoriteMixin import ToggleFavoriteMixin
from core.models import Email, Mailbox
from core.utils.fetchers.exceptions import FetcherError

from ..filters import MailboxFilterSet
from ..mixins.NoCreateMixin import NoCreateMixin
from ..serializers import MailboxWithDaemonSerializer


if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request


class MailboxViewSet(
    NoCreateMixin, viewsets.ModelViewSet[Mailbox], ToggleFavoriteMixin
):
    """Viewset for the :class:`core.models.Mailbox.Mailbox`.

    Provides all but the create action.
    """

    BASENAME = Mailbox.BASENAME
    serializer_class = MailboxWithDaemonSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MailboxFilterSet
    permission_classes = [IsAuthenticated]
    ordering_fields: Final[list[str]] = [
        "name",
        "account__mail_address",
        "account__mail_host",
        "account__protocol",
        "save_attachments",
        "save_to_eml",
        "is_favorite",
        "is_healthy",
        "created",
        "updated",
    ]
    ordering: Final[list[str]] = ["id"]

    @override
    def get_queryset(self) -> QuerySet[Mailbox]:
        """Filters the data for entries connected to the request user.

        Returns:
            The mailbox entries matching the request user.
        """
        if getattr(self, "swagger_fake_view", False):
            return Mailbox.objects.none()
        return Mailbox.objects.filter(  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
            account__user=self.request.user
        ).prefetch_related(
            "daemons"
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
            A response containing the updated mailbox data and the test result.
        """
        mailbox = self.get_object()
        response = Response(
            {
                "detail": _("Tested mailbox"),
            }
        )
        try:
            mailbox.test()
        except FetcherError as error:
            response.data["result"] = False
            response.data["error"] = str(error)
        else:
            response.data["result"] = True
        mailbox.refresh_from_db()
        response.data["mailbox"] = self.get_serializer(mailbox).data
        return response

    URL_PATH_FETCHING_OPTIONS = "fetching-options"
    URL_NAME_FETCHING_OPTIONS = "fetching-options"

    @action(
        detail=True,
        methods=["get"],
        url_path=URL_PATH_FETCHING_OPTIONS,
        url_name=URL_NAME_FETCHING_OPTIONS,
    )
    def fetching_options(self, request: Request, pk: int | None = None) -> Response:
        """Action method returning all fetching options for the mailbox.

        Args:
            request: The request triggering the action.
            pk: int: The private key of the mailbox. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        mailbox = self.get_object()

        available_fetching_options = mailbox.available_fetching_criteria
        return Response({"options": available_fetching_options})

    URL_PATH_FETCH = "fetch"
    URL_NAME_FETCH = "fetch"

    @action(
        detail=True,
        methods=["post"],
        url_path=URL_PATH_FETCH,
        url_name=URL_NAME_FETCH,
    )
    def fetch(self, request: Request, pk: int | None = None) -> Response:
        """Action method fetching all mails from the mailbox.

        Args:
            request: The request triggering the action.
            pk: The private key of the mailbox. Defaults to None.

        Returns:
            A response with the mailbox data.
        """
        mailbox = self.get_object()
        criterion = request.data.get("criterion")
        if not criterion:
            return Response(
                {"detail": _("Fetching criterion missing in request.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if criterion not in mailbox.available_fetching_criteria:
            return Response(
                {
                    "detail": _(
                        "The given fetching criterion is not available for this mailbox."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            mailbox.fetch(criterion)
        except FetcherError as error:
            response = Response(
                {
                    "detail": _("Error with mailaccount or mailbox occurred."),
                    "error": str(error),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            response = Response({"detail": _("All emails fetched.")})
        mailbox.refresh_from_db()
        response.data["mailbox"] = self.get_serializer(mailbox).data
        return response

    URL_PATH_DOWNLOAD = "download"
    URL_NAME_DOWNLOAD = "download"

    @action(
        detail=True,
        methods=["get"],
        url_path=URL_PATH_DOWNLOAD,
        url_name=URL_NAME_DOWNLOAD,
    )
    def download(
        self, request: Request, pk: int | None = None
    ) -> Response | FileResponse:
        """Action method downloading the eml files of all emails in the mailbox in a single file.

        Args:
            request: The request triggering the action.
            pk: The private key of the attachment to download. Defaults to None.

        Raises:
            Http404: If there are no emails in the mailbox.

        Returns:
            A fileresponse containing the emails in the requested format.
            A 400 response if file_format or id param are missing in the request.
        """
        file_format = request.query_params.get("file_format", None)
        if not file_format:
            return Response(
                {"detail": _("File format missing in request.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        mailbox = self.get_object()
        try:
            file = Email.queryset_as_file(mailbox.emails.all(), file_format)
        except ValueError:
            return Response(
                {
                    "detail": _("File format %(file_format)s is not supported.")
                    % {"file_format": file_format}
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Email.DoesNotExist:
            raise Http404(_("No emails found.")) from None
        else:
            return FileResponse(
                file,
                as_attachment=True,
                filename=mailbox.name + "." + file_format.split("[", maxsplit=1)[0],
            )

    URL_PATH_UPLOAD_MAILBOX = "upload"
    URL_NAME_UPLOAD_MAILBOX = "upload"

    @action(
        detail=True,
        methods=["post"],
        url_path=URL_PATH_UPLOAD_MAILBOX,
        url_name=URL_NAME_UPLOAD_MAILBOX,
    )
    def upload_emails(self, request: Request, pk: int | None = None) -> Response:
        """Action method allowing upload of a mailbox file and adding the contained mails to a mailbox.

        Args:
            request: The request triggering the action.
            pk: int: The private key of the mailbox to upload to. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        file_format = request.data.get("format", None)
        if file_format is None:
            return Response(
                {
                    "detail": _("File format %(file_format)s is not supported.")
                    % {"file_format": file_format}
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        uploaded_file = request.FILES.get("file", None)
        if uploaded_file is None:
            return Response(
                {"detail": _("File missing in request.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        mailbox = self.get_object()
        try:
            mailbox.add_emails_from_file(uploaded_file, file_format)
        except ValueError as error:
            return Response(
                {
                    "detail": _("An error occurred while processing the file."),
                    "error": str(error),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        mailbox_serializer = self.get_serializer(mailbox)
        return Response(
            {
                "detail": _("Successfully uploaded mailbox file."),
                "mailbox": mailbox_serializer.data,
            }
        )
