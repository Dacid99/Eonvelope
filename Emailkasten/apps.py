from django.apps import AppConfig


class EmailkastenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Emailkasten'

    def ready(self):
        from .signals import (
            delete_AttachmentModel, delete_DaemonModel, delete_EMailModel,
            delete_ImageModel, save_AccountModel, save_DaemonModel,
            save_MailboxModel)
