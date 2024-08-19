from django.db import models
from ..Fetchers.IMAPFetcher import IMAPFetcher
from ..Fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from ..Fetchers.POP3Fetcher import POP3Fetcher
from ..Fetchers.POP3_SSL_Fetcher import POP3_SSL_Fetcher
from ..Fetchers.ExchangeFetcher import ExchangeFetcher
from .UserModel import UserModel


class AccountModel(models.Model):
    mail_address = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    mail_host = models.CharField(max_length=255)
    mail_host_port = models.IntegerField(null=True)
    protocolChoices = {
        IMAPFetcher.PROTOCOL : "IMAP", 
        IMAP_SSL_Fetcher.PROTOCOL : "IMAP SSL",
        POP3Fetcher.PROTOCOL : "POP3",
        POP3_SSL_Fetcher.PROTOCOL : "POP3 SSL",
        ExchangeFetcher.PROTOCOL : "Exchange"
    }
    protocol = models.CharField(choices=protocolChoices, max_length=10)
    user = models.ForeignKey(UserModel, related_name='user' ,on_delete=models.CASCADE)

    def __str__(self):
        return f"Account {self.mail_address} with protocol {self.protocol}"

    class Meta:
        db_table = "accounts"

