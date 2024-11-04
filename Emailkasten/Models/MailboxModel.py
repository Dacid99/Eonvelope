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

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from ..constants import FetchingConfiguration, MailFetchingCriteria
from ..Fetchers.IMAPFetcher import IMAPFetcher
from ..Fetchers.POP3Fetcher import POP3Fetcher
from .AccountModel import AccountModel


logger = logging.getLogger(__name__)
"""The logger instance for this module."""

class MailboxModel(models.Model):
    """Database model for a mailbox in a mail account."""

    name = models.CharField(max_length=255)
    """The mailaccount internal name of the mailbox. Unique together with :attr:`account`."""

    account = models.ForeignKey(AccountModel, related_name="mailboxes", on_delete=models.CASCADE)
    """The mailaccount this mailbox was found in. Unique together with :attr:`name`. Deletion of that `account` deletes this mailbox."""

    FETCHINGCHOICES = dict(MailFetchingCriteria())
    """The available mail fetching criteria. Refers to :class:`Emailkasten.constants.MailFetchingCriteria`."""

    fetching_criterion = models.CharField(choices=FETCHINGCHOICES, default=MailFetchingCriteria.ALL, max_length=10)
    """The fetching criterion for this mailbox. One of :attr:`FETCHING_CHOICES`. :attr:`Emailkasten.constants.MailFetchingCriteria.ALL` by default."""

    save_attachments = models.BooleanField(default=FetchingConfiguration.SAVE_ATTACHMENTS_DEFAULT)
    """Whether to save attachments of the mails found in this mailbox. :attr:`Emailkasten.constants.FetchingConfiguration.SAVE_ATTACHMENTS_DEFAULT` by default."""

    save_images = models.BooleanField(default=FetchingConfiguration.SAVE_IMAGES_DEFAULT)
    """Whether to save images of the mails found in this mailbox. :attr:`Emailkasten.constants.FetchingConfiguration.SAVE_IMAGES_DEFAULT` by default."""

    save_toEML = models.BooleanField(default=FetchingConfiguration.SAVE_TO_EML_DEFAULT)
    """Whether to save the mails found in this mailbox as .eml files. :attr:`Emailkasten.constants.FetchingConfiguration.SAVE_TO_EML_DEFAULT` by default."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite mailboxes. False by default."""

    is_healthy = models.BooleanField(default=True)
    """Flags whether the mailbox can be accessed and read. True by default. 
    When the :attr:`Emailkasten.Models.AccountModel.is_healthy` field changes to `False`, this field is updated accordingly.
    When this field becomes `True` after being `False`, the :attr:`Emailkasten.Models.AccountModel.is_healthy` field of :attr:`account` will be set to `True` as well."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""


    def __str__(self):
        return f"Mailbox {self.name} of {self.account}"

    def getAvailableFetchingCriteria(self):
        """Gets the available fetching criteria based on the mail protocol of this mailbox. 
        Used by :func:`Emailkasten.Views.MailboxViewSet.fetching_options` to show the choices for fetching to the user.

        Returns:
            list: A list of all available fetching criteria for this mailbox. Empty if the protocol is unknown.
        """
        if self.account.protocol.startswith(IMAPFetcher.PROTOCOL):
            availableFetchingOptions = IMAPFetcher.AVAILABLE_FETCHING_CRITERIA
        elif self.account.protocol.startswith(POP3Fetcher.PROTOCOL):
            availableFetchingOptions = POP3Fetcher.AVAILABLE_FETCHING_CRITERIA
        else:
            availableFetchingOptions = []
        return availableFetchingOptions
    

    class Meta:
        db_table = "mailboxes"
        """The name of the database table for the mailboxes."""

        unique_together = ('name', 'account')
        """:attr:`name` and :attr:`account` in combination are unique."""



@receiver(post_save, sender=MailboxModel)
def post_save_is_healthy(sender, instance, **kwargs):
    """Receiver function flagging the account of a mailbox as healthy once that mailbox becomes healthy again.

    Args:
        sender (type): The class type that sent the post_save signal.
        instance (:class:`Emailkasten.Models.MailboxModel`): The instance that has been saved.
    
    Returns:
        None
    """
    if instance.is_healthy:
        try:
            oldInstance = MailboxModel.objects.get(pk=instance.pk)
            if oldInstance.is_healthy != instance.is_healthy :
                logger.debug(f"{str(instance)} has become healthy, flagging its account as healthy ...")
                instance.account.update(is_healthy=instance.is_healthy)
                logger.debug("Successfully flagged account as healthy.")

        except MailboxModel.DoesNotExist:
            logger.debug(f"Previous instance of {str(instance)} not found, no health flag comparison possible.")