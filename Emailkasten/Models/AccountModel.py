from django.db import models
from .IMAPFetcher import IMAPFetcher
from .IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from .POP3Fetcher import POP3Fetcher
from .POP3_SSL_Fetcher import POP3_SSL_Fetcher


class AccountModel(models.Model):
    user_name = models.CharField(max_length=255, not_null=True, unique=True)
    user_password = models.CharField(max_length=255, not_null=True)
    mail_host = models.CharField(max_length=255)
    mail_host_port = models.IntegerField()
    protocol = models.TextChoices(IMAPFetcher.PROTOCOL, IMAP_SSL_Fetcher.PROTOCOL, POP3Fetcher.PROTOCOL, POP3_SSL_Fetcher.PROTOCOL, ExchangeFetcher.PROTOCOL, not_null=True)
    cycle_interval = models.IntegerField(default=EMailArchiverDaemon.cyclePeriod, not_null=True)
    save_attachments = models.BooleanField(default=True, not_null=True)
    save_toEML = models.BooleanField(default=True, not_null=True)

    def __str__(self):
        return f"Account {self.user_name} with protocol {self.protocol}"

    class Meta:
        db_table = "accounts"

