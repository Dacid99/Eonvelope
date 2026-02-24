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

"""Module with the :class:`AccountViewSet` viewset."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final, override

from django.http import FileResponse, Http404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import BooleanField, CharField

from api.v1.filters import AccountFilterSet
from api.v1.mixins.ToggleFavoriteMixin import ToggleFavoriteMixin
from api.v1.serializers import AccountSerializer
from core.constants import SupportedEmailDownloadFormats
from core.models import Account, Mailbox
from core.utils.fetchers.exceptions import MailAccountError

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request


@extend_schema_view(
    list=extend_schema(description=_("Lists all instances matching the filter.")),
    retrieve=extend_schema(description=_("Retrieves a single instance.")),
    update=extend_schema(description=_("Updates a single instance.")),
    create=extend_schema(description=_("Creates a new instance.")),
    destroy=extend_schema(description=_("Deletes a single instance.")),
    update_mailboxes=extend_schema(
        request=None,
        responses={
            200: inline_serializer(
                name="update_mailboxes_account_response",
                fields={
                    "detail": CharField(),
                    "data": AccountSerializer(),
                },
            )
        },
        description=_("Updates the mailboxes of an account."),
    ),
    add_daemons=extend_schema(
        request=None,
        responses={
            200: inline_serializer(
                name="add_daemons_response",
                fields={"detail": CharField()},
            )
        },
        description=_(
            "Adds a standard set of routines for archiving all traffic to an account."
        ),
    ),
    test=extend_schema(
        request=None,
        responses={
            200: inline_serializer(
                name="test_account_response",
                fields={
                    "detail": CharField(),
                    "result": BooleanField(),
                    "data": AccountSerializer(),
                },
            )
        },
        description=_("Tests an account."),
    ),
    download=extend_schema(
        parameters=[
            OpenApiParameter(
                name="file_format",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                enum=SupportedEmailDownloadFormats.values,
            ),
        ],
        request=None,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="content-disposition: attachment",
            )
        },
        description=_("Downloads all emails of an account."),
    ),
)
class AccountViewSet(viewsets.ModelViewSet[Account], ToggleFavoriteMixin):
    """Viewset for the :class:`core.models.Account`.

    Provides all actions.
    """

    BASENAME = Account.BASENAME
    serializer_class = AccountSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AccountFilterSet
    permission_classes = [IsAuthenticated]
    ordering_fields: Final[list[str]] = [
        "mail_address",
        "mail_host",
        "mail_host_port",
        "protocol",
        "timeout",
        "is_healthy",
        "is_favorite",
        "created",
        "updated",
    ]
    ordering: Final[list[str]] = ["id"]

    @override
    def get_queryset(self) -> QuerySet[Account]:
        """Fetches the queryset by filtering the data for entries connected to the request user.

        Returns:
            The account entries matching the request user.
        """
        if getattr(self, "swagger_fake_view", False):
            return Account.objects.none()
        return Account.objects.filter(  # type: ignore[misc]  # user auth is checked by permissions, we also test for this
            user=self.request.user
        ).prefetch_related(
            "mailboxes"
        )

    URL_PATH_UPDATE_MAILBOXES = "update-mailboxes"
    URL_NAME_UPDATE_MAILBOXES = "update-mailboxes"

    @action(
        detail=True,
        methods=["post"],
        url_path=URL_PATH_UPDATE_MAILBOXES,
        url_name=URL_NAME_UPDATE_MAILBOXES,
    )
    def update_mailboxes(self, request: Request, pk: int | None = None) -> Response:
        """Action method updating the mailboxes in the account.

        Args:
            request: The request triggering the action.
            pk: The private key of the account to scan for mailboxes. Defaults to None.

        Returns:
            A response containing the updated account data.
        """
        account = self.get_object()
        try:
            account.update_mailboxes()
        except MailAccountError as error:
            response = Response(
                data={
                    "detail": _("An error with the mailaccount occurred."),
                    "error": str(error),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            response = Response(data={"detail": _("Updated mailboxes")})
        account.refresh_from_db()
        response.data["data"] = self.get_serializer(account).data
        return response

    URL_PATH_ADD_DAEMONS = "add-routines"
    URL_NAME_ADD_DAEMONS = "add-daemons"

    @action(
        detail=True,
        methods=["post"],
        url_path=URL_PATH_ADD_DAEMONS,
        url_name=URL_NAME_ADD_DAEMONS,
    )
    def add_daemons(self, request: Request, pk: int | None = None) -> Response:
        """Action method updating the mailboxes in the account.

        Args:
            request: The request triggering the action.
            pk: The private key of the account to scan for mailboxes. Defaults to None.

        Returns:
            A response containing the updated account data.
        """
        account = self.get_object()
        account.add_daemons()
        return Response(data={"detail": _("Added routines to inbox and sentbox.")})

    URL_PATH_TEST = "test"
    URL_NAME_TEST = "test"

    @action(
        detail=True, methods=["post"], url_path=URL_PATH_TEST, url_name=URL_NAME_TEST
    )
    def test(self, request: Request, pk: int | None = None) -> Response:
        """Action method testing the account data.

        Args:
            request: The request triggering the action.
            pk: The private key of the account to test. Defaults to None.

        Returns:
            A response containing the updated account data and the test result.
        """
        account = self.get_object()
        response = Response(
            {
                "detail": _("Tested mailaccount"),
            }
        )
        try:
            account.test()
        except MailAccountError as error:
            response.data["result"] = False
            response.data["error"] = str(error)
        else:
            response.data["result"] = True
        account.refresh_from_db()
        response.data["data"] = self.get_serializer(account).data
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
        """Action method downloading the eml files of all emails in the account in a single file.

        Args:
            request: The request triggering the action.
            pk: The private key of the account to download. Defaults to None.

        Raises:
            Http404: If there are no mailboxes in the account.
            ValidationError: If file_format is missing or unsupported.

        Returns:
            A fileresponse containing the mailboxes in the requested format.
        """
        file_format = request.query_params.get("file_format", None)
        if not file_format:
            raise ValidationError(
                {"file_format": _("File format is required.")},
            )
        account = self.get_object()
        try:
            file = Mailbox.queryset_as_file(account.mailboxes.all(), file_format)
        except ValueError:
            raise ValidationError(
                {
                    "file_format": _("File format %(file_format)s is not supported.")
                    % {"file_format": file_format}
                },
            ) from None
        except Mailbox.DoesNotExist:
            raise Http404(_("No mailboxes found.")) from None
        return FileResponse(
            file,
            as_attachment=True,
            filename=account.complete_mail_address + ".zip",
        )
