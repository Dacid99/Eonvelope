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
import os

from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .. import constants
from ..EMailArchiverDaemon import EMailArchiverDaemon
from ..Filters.MailboxFilter import MailboxFilter
from ..mailProcessing import fetchMails
from ..Models.MailboxModel import MailboxModel
from ..Serializers.MailboxSerializers.MailboxWithDaemonSerializer import \
    MailboxWithDaemonSerializer


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


    @action(detail=True, methods=['post'], url_path='daemon/test')
    def test_daemon(self, request, pk=None):
        mailbox = self.get_object()
        return EMailArchiverDaemon.testDaemon(mailbox.daemon)


    @action(detail=True, methods=['post'], url_path='daemon/start')
    def start_daemon(self, request, pk=None):
        mailbox = self.get_object()
        return EMailArchiverDaemon.startDaemon(mailbox.daemon)


    @action(detail=True, methods=['post'], url_path='daemon/stop')
    def stop_daemon(self, request, pk=None):
        mailbox = self.get_object()
        return EMailArchiverDaemon.stopDaemon(mailbox.daemon)


    @action(detail=True, methods=['post'])
    def fetch_all(self, request, pk=None):
        mailbox = self.get_object()

        fetchMails(mailbox, mailbox.account, constants.MailFetchingCriteria.ALL)

        mailboxSerializer = self.get_serializer(mailbox)
        return Response({'status': 'All mails fetched', "mailbox": mailboxSerializer.data})


    @action(detail=True, methods=['get'])
    def fetching_options(self, request, pk=None):
        mailbox = self.get_object()

        availableFetchingOptions = mailbox.getAvailableFetchingCriteria()
        if availableFetchingOptions:
            return Response({'options': availableFetchingOptions})
        else:
            return Response({'error': "No fetching options available for this mailbox!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=True, methods=['post'], url_path='toggle_favorite')
    def toggle_favorite(self, request, pk=None):
        mailbox = self.get_object()
        mailbox.is_favorite = not mailbox.is_favorite
        mailbox.save()
        return Response({'status': 'Mailbox marked as favorite'})


    @action(detail=False, methods=['get'], url_path='favorites')
    def favorites(self, request):
        favoriteMailboxes = MailboxModel.objects.filter(is_favorite=True)
        serializer = self.get_serializer(favoriteMailboxes, many=True)
        return Response(serializer.data)


    @action(detail=True, methods=['get'], url_path='daemon/log/download')
    def log_download(self, request, pk=None):
        mailbox = self.get_object()
        daemonLogFilepath = mailbox.dameon.log_filepath
        daemonLogFilename = os.path.basename(daemonLogFilepath)

        if not os.path.exists(daemonLogFilepath):
            raise Http404("Log file not found")

        response = FileResponse(open(daemonLogFilepath, 'rb'), as_attachment=True, filename=daemonLogFilename)
        return response
