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

from typing import TYPE_CHECKING

from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..constants import TestStatusCodes
from ..Filters.AccountFilter import AccountFilter
from ..mailProcessing import scanMailboxes, testAccount
from ..Models.AccountModel import AccountModel
from ..Serializers.AccountSerializers.AccountSerializer import \
    AccountSerializer

if TYPE_CHECKING:
    from django.db.models import BaseManager
    from rest_framework.request import Request
    from rest_framework.serializers import BaseSerializer


class AccountViewSet(viewsets.ModelViewSet):
    """Viewset for the :class:`Emailkasten.Models.AccountModel.AccountModel`."""

    queryset = AccountModel.objects.all()
    serializer_class = AccountSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = AccountFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['mail_address', 'mail_host', 'protocol', 'created', 'updated']
    ordering = ['id']


    def get_queryset(self) -> BaseManager[AccountModel]:
        """Filters the data for entries connected to the request user.

        Returns:
            The account entries matching the request user."""
        return AccountModel.objects.filter(user = self.request.user)


    def perform_create(self, serializer: BaseSerializer):
        """Adds the request user to the serializer data of the create request.

        Args:
            serializer: The serializer data of the create request.
        """
        try:
            serializer.save(user = self.request.user)
            return None
        except IntegrityError:
            return Response({'detail': 'This account already exists!'}, status=status.HTTP_409_CONFLICT)


    @action(detail=True, methods=['post'])
    def scan_mailboxes(self, request: Request, pk: int|None=None) -> Response:
        """Action method scanning for mailboxes in the account.

        Args:
            request: The request triggering the action.
            pk: The private key of the account to scan for mailboxes. Defaults to None.

        Returns:
            A response containing the updated account data.
        """
        account = self.get_object()
        scanMailboxes(account)

        accountSerializer = self.get_serializer(account)
        return Response(data = {'status': 'Scanned for mailboxes', 'account': accountSerializer.data})


    @action(detail=True, methods=['post'], url_path='test')
    def test(self, request: Request, pk: int|None =None) -> Response:
        """Action method testing the account data.

        Args:
            request: The request triggering the action.
            pk: The private key of the account to test. Defaults to None.

        Returns:
            A response containing the updated account data and the test resultcode.
        """
        account = self.get_object()
        result = testAccount(account)

        accountSerializer = self.get_serializer(account)
        return Response({'status': 'Tested mailaccount', 'account': accountSerializer.data, 'result': TestStatusCodes.INFOS[result]})


    @action(detail=True, methods=['post'], url_path='toggle_favorite')
    def toggle_favorite(self, request: Request, pk: int|None = None) -> Response:
        """Action method toggling the favorite flag of the account.

        Args:
            request: The request triggering the action.
            pk: The private key of the account to toggle favorite. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        account = self.get_object()
        account.is_favorite = not account.is_favorite
        account.save(update_fields=['is_favorite'])
        return Response({'status': 'Account marked as favorite'})


    @action(detail=False, methods=['get'], url_path='favorites')
    def favorites(self, request: Request) -> Response:
        """Action method returning all accounts with favorite flag.

        Args:
            request: The request triggering the action.

        Returns:
            A response containing all account data with favorite flag.
        """
        favoriteAccounts = AccountModel.objects.filter(is_favorite=True)
        serializer = self.get_serializer(favoriteAccounts, many=True)
        return Response(serializer.data)
