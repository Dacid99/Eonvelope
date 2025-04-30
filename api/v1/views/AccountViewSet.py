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

"""Module with the :class:`AccountViewSet` viewset."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final, override

from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.mixins.ToggleFavoriteMixin import ToggleFavoriteMixin
from core.models.AccountModel import AccountModel
from core.utils.fetchers.exceptions import MailAccountError

from ..filters.AccountFilter import AccountFilter
from ..serializers.account_serializers.AccountSerializer import AccountSerializer


if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from rest_framework.request import Request
    from rest_framework.serializers import BaseSerializer


class AccountViewSet(viewsets.ModelViewSet[AccountModel], ToggleFavoriteMixin):
    """Viewset for the :class:`core.models.AccountModel.AccountModel`."""

    BASENAME = AccountModel.BASENAME
    serializer_class = AccountSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AccountFilter
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
    def get_queryset(self) -> QuerySet[AccountModel]:
        """Fetches the queryset by filtering the data for entries connected to the request user.

        Returns:
            The account entries matching the request user.
        """
        if getattr(self, "swagger_fake_view", False):
            return AccountModel.objects.none()
        if not self.request.user.is_authenticated:
            return AccountModel.objects.none()
        return AccountModel.objects.filter(user=self.request.user)

    @override
    def perform_create(self, serializer: BaseSerializer[AccountModel]) -> None:
        """Adds the request user to the serializer data of the create request.

        Args:
            serializer: The serializer data of the create request.

        Raises:
            ValidationError: If an IntegrityError occurs.
        """
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            # pylint: disable-next=raise-missing-from  # raising with from is unnecessary here
            raise ValidationError(  # noqa: B904
                {"detail": "This account already exists!"}
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
        accountSerializer = self.get_serializer(account)
        try:
            account.update_mailboxes()
        except MailAccountError as error:
            return Response(
                data={
                    "detail": "Error with mailaccount occured!",
                    "account": accountSerializer.data,
                    "error": str(error),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            data={"detail": "Updated mailboxes", "account": accountSerializer.data}
        )

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
        accountSerializer = self.get_serializer(account)
        response = Response(
            {
                "detail": "Tested mailaccount",
                "account": accountSerializer.data,
            }
        )
        try:
            account.test_connection()
        except MailAccountError as error:
            response.data["result"] = False
            response.data["error"] = str(error)
        else:
            response.data["result"] = True
        return response
