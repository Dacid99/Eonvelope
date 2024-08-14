from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..Models.AccountModel import AccountModel
from ..Serializers import AccountSerializer
from ..MailProcessor import MailProcessor
from ..EMailDBFeeder import EMailDBFeeder

class AccountViewSet(viewsets.ModelViewSet):
    queryset = AccountModel.objects.all()
    serializer_class = AccountSerializer

    @action(detail=True, methods=['post'])
    def scan_mailboxes(self, request, pk=None):
        account = self.get_object()
        mailboxesList = MailProcessor.scanMailboxes(account)
        
        EMailDBFeeder.insertMailboxes(mailboxesList, account)
        
        return Response({'status': 'Scanned for mailboxes', 'account': mailbox.account.mail_address, 'found mailboxes': mailboxesList})

