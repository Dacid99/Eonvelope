from rest_framework import viewsets
from AccountModel import AccountModel
from Serializers import AccountSerializer

class AccountViewSet(viewsets.ModelViewSet):
    queryset = AccountModel.objects.all()
    serializer_class = AccountSerializer

    activeEmailArchiverDaemons = {}

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        account = self.get_object()
        if account.mail_address not in self.activeEmailArchiverDaemons:
            daemon = EMailArchiverDaemon(account).start()
            self.activeEmailArchiverDaemons[account.mail_address] = daemon
            account.is_fetched = True
            account.save()
            return Response({'status': 'Daemon started', 'account': account.mail_address})
        else:
            return Response({'status': 'Daemon already running', 'account': account.mail_address})

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        account = self.get_object() 
        if account.mail_address in self.activeEmailArchiverDaemons:
            daemon = self.activeEmailArchiverDaemons.pop(account.mail_address)
            daemon.stop()
            account.is_fetched = False
            account.save()
            return Response({'status': 'Daemon stopped', 'account': account.mail_address})
        else:
            return Response({'status': 'Daemon not running', 'account': account.mail_address})