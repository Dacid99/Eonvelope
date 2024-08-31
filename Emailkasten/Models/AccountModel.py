from django.db import models
from django.contrib.auth.models import User
from .. import constants

class AccountModel(models.Model):
    mail_address = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    mail_host = models.CharField(max_length=255)
    mail_host_port = models.IntegerField(null=True)
    protocolChoices = {
        constants.MailFetchingProtocols.IMAP : "IMAP", 
        constants.MailFetchingProtocols.IMAP_SSL : "IMAP SSL",
        constants.MailFetchingProtocols.POP3 : "POP3",
        constants.MailFetchingProtocols.POP3_SSL : "POP3 SSL",
        constants.MailFetchingProtocols.EXCHANGE : "Exchange"
    }
    protocol = models.CharField(choices=protocolChoices, max_length=10)
    is_healthy = models.BooleanField(default=True)
    user = models.ForeignKey(User, related_name='accounts', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Account {self.mail_address} at host {self.mail_host}:{self.mail_host_port} with protocol {self.protocol}"

    class Meta:
        db_table = "accounts"

