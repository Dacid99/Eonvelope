from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .Models.MailboxModel import MailboxModel
from .ViewSets.MailboxViewSet import MailboxViewSet
import logging

@receiver(post_migrate)
def startDaemonsOnStartup(sender, **kwargs):        
    logging.info(f"Restarting daemons on startup")
    mailboxViewSet = MailboxViewSet()
    mailboxesWithDaemons = MailboxModel.objects.filter(is_fetched=True)

    for mailbox in mailboxesWithDaemons:
        try:
            mailboxViewSet.startDaemon(mailbox)
        except Exception:
            logging.error("Failed to start daemon on restart!")
    logging.info("Done restarting daemons")