# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .. import constants


logger = logging.getLogger(__name__)
"""The logger instance for this module."""

class AccountModel(models.Model):
    """Database model for the account data of a mail account."""

    mail_address = models.EmailField(max_length=255)
    """The mail address of the account. Unique together with :attr:`user`."""

    password = models.CharField(max_length=255)
    """The password to log into the account."""

    mail_host = models.CharField(max_length=255)
    """The url of the mail server where the account is located."""

    mail_host_port = models.IntegerField(null=True)
    """The port of the mail server. Can be null if the default port of the protocol is used."""

    PROTOCOL_CHOICES = {
        constants.MailFetchingProtocols.IMAP : "IMAP",
        constants.MailFetchingProtocols.IMAP_SSL : "IMAP SSL",
        constants.MailFetchingProtocols.POP3 : "POP3",
        constants.MailFetchingProtocols.POP3_SSL : "POP3 SSL",
        constants.MailFetchingProtocols.EXCHANGE : "Exchange"
    }
    """The available mail protocols."""

    protocol = models.CharField(choices=PROTOCOL_CHOICES, max_length=10)
    """The mail protocol of the mail server. One of :attr:`PROTOCOL_CHOICES`."""

    timeout = models.IntegerField(null=True)
    """The timeout parameter for the connection to the host. Can be null."""

    is_healthy = models.BooleanField(default=True)
    """Flags whether the account can be accessed using the data. True by default.
    When this field changes to `False`, all mailboxes :attr:`Emailkasten.Models.MailboxModel.is_healthy` field will be updated accordingly.
    When the :attr:`Emailkasten.Models.MailboxModel.is_healthy` field of one of the mailboxes referencing this entry via :attr:`Emailkasten.Models.MailboxModel.account`
    becomes `True` after being `False`, this field will be set to `True` as well."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite accounts. False by default."""

    user = models.ForeignKey(User, related_name='accounts', on_delete=models.CASCADE)
    """The user this account belongs to. Deletion of that `user` deletes this correspondent."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""


    def __str__(self):
        return f"Account {self.mail_address} at host {self.mail_host}:{self.mail_host_port} with protocol {self.protocol}"

    class Meta:
        db_table = "accounts"
        """The name of the database table for the mail accounts."""

        unique_together = ("mail_address", "user")
        """`mail_address` and :attr:`user` in combination are unique fields."""



@receiver(post_save, sender=AccountModel)
def post_save_is_healthy(sender: AccountModel, instance: AccountModel, **kwargs) -> None:
    """Receiver function flagging all mailboxes of an account as unhealthy once that account becomes unhealthy.

    Args:
        sender: The class type that sent the post_save signal.
        instance: The instance that has been saved.
        **kwargs: Other keyword arguments.
    """
    if not instance.is_healthy:
        try:
            oldInstance = AccountModel.objects.get(pk=instance.pk)
            if oldInstance.is_healthy:
                logger.debug("%s has become unhealthy, flagging all its mailboxes as unhealthy ...", str(instance))
                mailboxEntries = instance.mailboxes.all()
                for mailboxEntry in mailboxEntries:
                    mailboxEntry.is_healthy = False
                    mailboxEntry.save(update_fields=['is_healthy'])
                logger.debug("Successfully flagged mailboxes as unhealthy.")

        except AccountModel.DoesNotExist:
            logger.debug("Previous instance of %s not found, no health flag comparison possible.", str(instance))
