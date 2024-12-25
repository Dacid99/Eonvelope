# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Module with the :class:`MailboxModel` model class."""

import logging

from dirtyfields import DirtyFieldsMixin
from django.db import models

from ..constants import FetchingConfiguration
from ..Fetchers.IMAPFetcher import IMAPFetcher
from ..Fetchers.POP3Fetcher import POP3Fetcher
from .AccountModel import AccountModel

logger = logging.getLogger(__name__)
"""The logger instance for this module."""

class MailboxModel(DirtyFieldsMixin, models.Model):
    """Database model for a mailbox in a mail account."""

    name = models.CharField(max_length=255)
    """The mailaccount internal name of the mailbox. Unique together with :attr:`account`."""

    account = models.ForeignKey(AccountModel, related_name="mailboxes", on_delete=models.CASCADE)
    """The mailaccount this mailbox was found in. Unique together with :attr:`name`. Deletion of that `account` deletes this mailbox."""

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
        """Metadata class for the model."""

        db_table = "mailboxes"
        """The name of the database table for the mailboxes."""

        unique_together = ('name', 'account')
        """:attr:`name` and :attr:`account` in combination are unique."""
