from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from ..Models.MailboxModel import MailboxModel
from ..Filters.MailboxFilter import MailboxFilter
from ..Serializers import MailboxSerializer, MailboxWithDaemonSerializer
from ..MailProcessor import MailProcessor
from .. import constants
import logging

class MailboxViewSet(viewsets.ModelViewSet):
    queryset = MailboxModel.objects.all()
    serializer_class = MailboxWithDaemonSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = MailboxFilter
    ordering_fields = ['name', 'account__mail_address', 'account__mail_host', 'account__protocol', 'created', 'updated']
    ordering = ['id']

    def get_queryset(self):
        return MailboxModel.objects.filter(account__user = self.request.user)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        mailbox = self.get_object()
        return mailbox.daemon.start()
    

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        mailbox = self.get_object() 
        return mailbox.daemon.stop()
    
    
    @action(detail=True, methods=['post'])
    def fetch_all(self, request, pk=None):
        mailbox = self.get_object() 
        
        MailProcessor.fetch(mailbox, mailbox.account, constants.MailFetchingCriteria.ALL)

        return Response({'status': 'All mails fetched', 'account': mailbox.account.mail_address, 'mailbox': mailbox.name})
