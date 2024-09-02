from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from ..Models.MailboxModel import MailboxModel
from ..Filters.MailboxFilter import MailboxFilter
from ..Serializers import MailboxSerializer
from ..EMailArchiverDaemon import EMailArchiverDaemon 
from ..MailProcessor import MailProcessor
from .. import constants
import logging

class MailboxViewSet(viewsets.ModelViewSet):
    queryset = MailboxModel.objects.all()
    serializer_class = MailboxSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = MailboxFilter
    ordering_fields = ['name', 'account__mail_address', 'account__mail_host', 'account__protocol', 'created', 'updated']
    ordering = ['id']

    activeEmailArchiverDaemons = {}

    def get_queryset(self):
        return MailboxModel.objects.filter(account__user = self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        mailbox = self.get_object()
        if mailbox.id not in self.activeEmailArchiverDaemons:
            try:
                self.startDaemon(mailbox)
                return Response({'status': 'Daemon started', 'account': mailbox.account.mail_address, 'mailbox': mailbox.name})
            except Exception as e:
                return Response({'status': 'Daemon failed to start!', 'account': mailbox.account.mail_address, 'mailbox': mailbox.name})
        else:
            return Response({'status': 'Daemon already running', 'account': mailbox.account.mail_address, 'mailbox': mailbox.name})

    def startDaemon(self, mailbox):
        try:
            daemon = EMailArchiverDaemon(mailbox)
            daemon.start()
            self.activeEmailArchiverDaemons[mailbox.id] = daemon
            mailbox.is_fetched = True
            mailbox.save()
        except Exception as e:
            logging.error(f"Could not start daemon for {str(mailbox)}!", exc_info=True)
            mailbox.is_fetched = False
            mailbox.save()
            raise e

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        mailbox = self.get_object() 
        if mailbox.id in self.activeEmailArchiverDaemons:
            daemon = self.activeEmailArchiverDaemons.pop(mailbox.id)
            daemon.stop()
            mailbox.is_fetched = False
            mailbox.save()
            return Response({'status': 'Daemon stopped', 'account': mailbox.account.mail_address, 'mailbox': mailbox.name})
        else:
            return Response({'status': 'Daemon not running', 'account': mailbox.account.mail_address, 'mailbox': mailbox.name})

    @action(detail=True, methods=['post'])
    def fetch_all(self, request, pk=None):
        mailbox = self.get_object() 
        
        MailProcessor.fetch(mailbox, mailbox.account, constants.MailFetchingCriteria.ALL)

        return Response({'status': 'All mails fetched', 'account': mailbox.account.mail_address, 'mailbox': mailbox.name})
