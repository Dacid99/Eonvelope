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

from core.utils.fetchers.IMAPFetcher import IMAPFetcher
from core.utils.fetchers.POP3Fetcher import POP3Fetcher
from Emailkasten.utils import get_config

from ..constants import TestStatusCodes

logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class MailboxModel(DirtyFieldsMixin, models.Model):
    """Database model for a mailbox in a mail account."""

    name = models.CharField(max_length=255)
    """The mailaccount internal name of the mailbox. Unique together with :attr:`account`."""

    account = models.ForeignKey(
        "AccountModel", related_name="mailboxes", on_delete=models.CASCADE
    )
    """The mailaccount this mailbox was found in. Unique together with :attr:`name`. Deletion of that `account` deletes this mailbox."""

    save_attachments = models.BooleanField(
        default=get_config("DEFAULT_SAVE_ATTACHMENTS")
    )
    """Whether to save attachments of the mails found in this mailbox. :attr:`constance.get_config('DEFAULT_SAVE_ATTACHMENTS')` by default."""

    save_images = models.BooleanField(default=get_config("DEFAULT_SAVE_IMAGES"))
    """Whether to save images of the mails found in this mailbox. :attr:`constance.get_config('DEFAULT_SAVE_IMAGES')` by default."""

    save_toEML = models.BooleanField(default=get_config("DEFAULT_SAVE_TO_EML"))
    """Whether to save the mails found in this mailbox as .eml files. :attr:`constance.get_config('DEFAULT_SAVE_TO_EML')` by default."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite mailboxes. False by default."""

    is_healthy = models.BooleanField(default=True)
    """Flags whether the mailbox can be accessed and read. True by default.
    When the :attr:`core.models.AccountModel.is_healthy` field changes to `False`, this field is updated accordingly.
    When this field becomes `True` after being `False`, the :attr:`core.models.AccountModel.is_healthy` field of :attr:`account` will be set to `True` as well."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""

    def __str__(self):
        return f"Mailbox {self.name} of {self.account}"

    def getAvailableFetchingCriteria(self):
        """Gets the available fetching criteria based on the mail protocol of this mailbox.
        Used by :func:`api.v1.views.MailboxViewSet.fetching_options` to show the choices for fetching to the user.

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

        constraints = [
            models.UniqueConstraint(
                fields=["name", "account"], name="mailbox_unique_together_name_account"
            )
        ]
        """:attr:`name` and :attr:`account` in combination are unique."""

    def test_connection(self):
        """Tests whether the data in the model is correct
        and allows connecting and logging in to the mailhost and account.
        The :attr:`core.models.MailboxModel.is_healthy` flag is set accordingly.
        Relies on the `test` method of the :mod:`core.utils.fetchers` classes.

        Returns:
            The resultcode of the test.
        """

        logger.info("Testing %s ...", self)
        try:
            with self.account.get_fetcher() as fetcher:
                result = fetcher.test(self)

        except ValueError:
            logger.error("Account %s has unknown protocol!", self)
            self.is_healthy = False
            self.save(update_fields=["is_healthy"])
            result = TestStatusCodes.ERROR

        logger.info("Successfully tested account to be %s.", result)
        return result

    def fetch(self, criterion):
        logger.info("Fetching emails with criterion %s from %s ...", criterion, self)
        with self.account.get_fetcher() as fetcher:
            fetchedMails = fetcher.fetchEmails(self, criterion)
        logger.info("Successfully fetched emails.")
        return fetchedMails
