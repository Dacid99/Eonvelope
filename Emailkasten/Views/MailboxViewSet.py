# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

from typing import TYPE_CHECKING

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .. import constants
from ..constants import TestStatusCodes
from ..Filters.MailboxFilter import MailboxFilter
from ..mailProcessing import fetchMails, testMailbox
from ..Models.MailboxModel import MailboxModel
from ..Models.DaemonModel import DaemonModel
from ..Serializers.MailboxSerializers.MailboxWithDaemonSerializer import \
    MailboxWithDaemonSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request



class MailboxViewSet(viewsets.ModelViewSet):
    queryset = MailboxModel.objects.all()
    serializer_class = MailboxWithDaemonSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = MailboxFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['name', 'account__mail_address', 'account__mail_host', 'account__protocol', 'created', 'updated']
    ordering = ['id']


    def get_queryset(self):
        return MailboxModel.objects.filter(account__user = self.request.user)


    @action(detail=True, methods='POST')
    def add_daemon(self, request: Request, pk: int|None = None) -> Response:
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
        return Response({'status': 'Added daemon for mailbox', 'mailbox': mailboxSerializer.data})


    @action(detail=True, methods=['post'], url_path='test')
    def test_mailbox(self, request: Request, pk:int|None = None) -> Response:
        """Action method testing the mailbox data.

        Args:
            request: The request triggering the action.
            pk: The private key of the mailbox to test. Defaults to None.

        Returns:
            A response containing the updated mailbox data and the test resultcode.
        """
        mailbox = self.get_object()
        result = testMailbox(mailbox)

        mailboxSerializer = self.get_serializer(mailbox)
        return Response({'status': 'Tested mailbox', 'mailbox': mailboxSerializer.data, 'result': TestStatusCodes.INFOS[result]})


    @action(detail=True, methods=['post'])
    def fetch_all(self, request: Request, pk: int|None = None) -> Response:
        """Action method fetching all mails from the mailbox.

        Args:
            request: The request triggering the action.
            pk: The private key of the mailbox. Defaults to None.

        Returns:
            A response with the mailbox data.
        """
        mailbox = self.get_object()

        fetchMails(mailbox, mailbox.account, constants.MailFetchingCriteria.ALL)

        mailboxSerializer = self.get_serializer(mailbox)
        return Response({'status': 'All mails fetched', "mailbox": mailboxSerializer.data})


    @action(detail=True, methods=['get'])
    def fetching_options(self, request: Request, pk: int|None = None) -> Response:
        """Action method returning all fetching options for the mailbox.

        Args:
            request: The request triggering the action.
            pk: int: The private key of the mailbox. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        mailbox = self.get_object()

        availableFetchingOptions = mailbox.getAvailableFetchingCriteria()
        if availableFetchingOptions:
            return Response({'options': availableFetchingOptions})
        else:
            return Response({'error': "No fetching options available for this mailbox!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=True, methods=['post'], url_path='toggle_favorite')
    def toggle_favorite(self, request: Request, pk: int|None = None) -> Response:
        """Action method toggling the favorite flag of the mailbox.

        Args:
            request: The request triggering the action.
            pk: int: The private key of the mailbox to toggle favorite. Defaults to None.

        Returns:
            A response detailing the request status.
        """
        mailbox = self.get_object()
        mailbox.is_favorite = not mailbox.is_favorite
        mailbox.save(update_fields=['is_favorite'])
        return Response({'status': 'Mailbox marked as favorite'})


    @action(detail=False, methods=['get'], url_path='favorites')
    def favorites(self, request: Request) -> Response:
        """Action method returning all mailboxes with favorite flag.

        Args:
            request: The request triggering the action.

        Returns:
            A response containing all mailbox data with favorite flag.
        """
        favoriteMailboxes = MailboxModel.objects.filter(is_favorite=True)
        serializer = self.get_serializer(favoriteMailboxes, many=True)
        return Response(serializer.data)
