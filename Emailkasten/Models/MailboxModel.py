from django.db import models
from ..MailProcessor import MailProcessor
from .AccountModel import AccountModel


class MailboxModel(models.Model):
    name = models.CharField(max_length=255)
    account = models.ForeignKey(AccountModel, related_name="account", on_delete=models.CASCADE)
    cycle_interval = models.IntegerField(default=60)
    fetchingChoices = {
        MailProcessor.RECENT : "recent", 
        MailProcessor.UNSEEN : "unseen",
        MailProcessor.ALL : "all"
    }
    fetching_criterion = models.CharField(choices=fetchingChoices, default=MailProcessor.RECENT, max_length=10)
    save_attachments = models.BooleanField(default=True)
    save_toEML = models.BooleanField(default=True)
    is_fetched = models.BooleanField(default=False)

    def __str__(self):
        return f"Mailbox {self.name} of {self.account}"

    class Meta:
        unique_together = ('name', 'account')
        db_table = "mailboxes"

