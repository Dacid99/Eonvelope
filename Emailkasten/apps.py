from django.apps import AppConfig
import logging

class Appconfig(AppConfig):
    name = 'Emailkasten'

    def ready(self):
        from .Models.MailboxModel import MailboxModel
        from .ViewSets.MailboxViewSet import MailboxViewSet
        
        logging.info(f"Restarting daemons in ready")
        mailboxViewSet = MailboxViewSet()
        mailboxesWithDaemons = MailboxModel.objects.filter(is_fetched=True)

        for mailbox in mailboxesWithDaemons:
            try:
                mailboxViewSet.startDaemon(mailbox)
            except Exception:
                logging.error("Failed to start daemon on restart!")
