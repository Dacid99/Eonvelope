from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..Models.AccountModel import AccountModel
from ..Filters.AccountFilter import AccountFilter
from ..Serializers import AccountSerializer
from ..MailProcessor import MailProcessor
from ..EMailDBFeeder import EMailDBFeeder

class AccountViewSet(viewsets.ModelViewSet):
    queryset = AccountModel.objects.all()
    serializer_class = AccountSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = AccountFilter
    ordering_fields = ['mail_address', 'mail_host', 'protocol', 'created', 'updated']
    ordering = ['id']
    permission_classes = [IsA]

    @action(detail=True, methods=['post'])
    def scan_mailboxes(self, request, pk=None):
        account = self.get_object()
        mailboxesList = MailProcessor.scanMailboxes(account)
        
        EMailDBFeeder.insertMailboxes(mailboxesList, account)
        
        return Response({'status': 'Scanned for mailboxes', 'account': account.mail_address, 'found mailboxes': mailboxesList})
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        account = self.get_object()
        result = MailProcessor.test(account)
        return Response({'status': 'Tested mailaccount', 'account': account.mail_address, 'result': result})

