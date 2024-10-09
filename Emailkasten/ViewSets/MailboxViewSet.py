'''
    Emailkasten - a open-source self-hostable email archiving server
    Copyright (C) 2024  David & Philipp Aderbauer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..Models.MailboxModel import MailboxModel
from ..Filters.MailboxFilter import MailboxFilter
from ..Serializers.MailboxSerializers.MailboxWithDaemonSerializer import MailboxWithDaemonSerializer
from ..EMailArchiverDaemon import EMailArchiverDaemon
from .. import constants
from ..mailProcessing import fetchMails


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
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        mailbox = self.get_object()
        return EMailArchiverDaemon.startDaemon(mailbox.daemon)
    

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        mailbox = self.get_object() 
        return EMailArchiverDaemon.stopDaemon(mailbox.daemon)
    
    
    @action(detail=True, methods=['post'])
    def fetch_all(self, request, pk=None):
        mailbox = self.get_object() 
        
        fetchMails(mailbox, mailbox.account, constants.MailFetchingCriteria.ALL)

        return Response({'status': 'All mails fetched', 'account': mailbox.account.mail_address, 'mailbox': mailbox.name})
    