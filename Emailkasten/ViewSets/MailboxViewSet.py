from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..Models.MailboxModel import MailboxModel
from ..Serializers import MailboxSerializer
from ..EMailArchiverDaemon import EMailArchiverDaemon 
from ..MailProcessor import MailProcessor
from ..EMailDBFeeder import EMailDBFeeder

class MailboxViewSet(viewsets.ModelViewSet):
    queryset = MailboxModel.objects.all()
    serializer_class = MailboxSerializer

    activeEmailArchiverDaemons = {}

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        mailbox = self.get_object()
        if mailbox.id not in self.activeEmailArchiverDaemons:
            daemon = EMailArchiverDaemon(mailbox)
            daemon.start()
            self.activeEmailArchiverDaemons[mailbox.id] = daemon
            mailbox.is_fetched = True
            mailbox.save()
            return Response({'status': 'Daemon started', 'account': mailbox.account.mail_address, 'mailbox': mailbox.name})
        else:
            return Response({'status': 'Daemon already running', 'account': mailbox.account.mail_address, 'mailbox': mailbox.name})

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
        
        MailProcessor.fetch(mailbox, mailbox.account, MailProcessor.ALL)

        return Response({'status': 'All mails fetched', 'account': mailbox.account.mail_address, 'mailbox': mailbox.name})
