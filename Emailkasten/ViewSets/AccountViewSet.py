from rest_framework import viewsets
from rest_framework.decorators import action
from ..Models.AccountModel import AccountModel
from ..Serializers import AccountSerializer
from ..EMailArchiverDaemon import EMailArchiverDaemon 

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

    @action(detail=True, methods=['post'])
    def fetch_all(self, request, pk=None):
        account = self.get_object() 
        try:
            with DBManager(EMailArchiverDaemon.dbHost, EMailArchiverDaemon.dbUser, EMailArchiverDaemon.dbPassword, "email_archive", "utf8mb4", "utf8mb4_bin") as db:
                dbfeeder = EMailDBFeeder(db)

                parsedMails = MailFetcher.fetch(account, MailFetcher.ALL)

                for mail in parsedNewMails:
                    EMailDBFeeder.insert(mail)
                        
        except Exception as e:
            raise

        return Response({'status': 'All mails fetched', 'account': account.mail_address})