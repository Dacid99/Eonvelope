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

from __future__ import annotations

import logging
import mailbox
import os
from typing import TYPE_CHECKING, Final

from dirtyfields import DirtyFieldsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.mixins.UploadMixin import UploadMixin
from core.mixins.URLMixin import URLMixin
from core.models.EMailModel import EMailModel
from Emailkasten.utils import get_config

from ..utils.fetchers.exceptions import MailAccountError, MailboxError
from ..utils.mailParsing import parseMailboxName


if TYPE_CHECKING:
    from .AccountModel import AccountModel


logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class MailboxModel(DirtyFieldsMixin, URLMixin, UploadMixin, models.Model):
    """Database model for a mailbox in a mail account."""

    name = models.CharField(max_length=255)
    """The mailaccount internal name of the mailbox. Unique together with :attr:`account`."""

    account: models.ForeignKey[AccountModel] = models.ForeignKey(
        "AccountModel", related_name="mailboxes", on_delete=models.CASCADE
    )
    """The mailaccount this mailbox was found in. Unique together with :attr:`name`. Deletion of that `account` deletes this mailbox."""

    save_attachments = models.BooleanField(
        default=get_config("DEFAULT_SAVE_ATTACHMENTS"),
        verbose_name=_("Save attachments"),
        help_text=_(
            "Whether the attachments from the emails in this mailbox will be saved."
        ),
    )
    """Whether to save attachments of the mails found in this mailbox. :attr:`constance.get_config('DEFAULT_SAVE_ATTACHMENTS')` by default."""

    save_toEML = models.BooleanField(
        default=get_config("DEFAULT_SAVE_TO_EML"),
        verbose_name=_("Save as .eml"),
        help_text=_("Whether the emails in this mailbox will be stored in .eml files."),
    )
    """Whether to save the mails found in this mailbox as .eml files. :attr:`constance.get_config('DEFAULT_SAVE_TO_EML')` by default."""

    save_toHTML = models.BooleanField(
        default=get_config("DEFAULT_SAVE_TO_HTML"),
        verbose_name=_("Save as .html"),
        help_text=_(
            "Whether the emails in this mailbox will be converted and stored in .html files."
        ),
    )
    """Whether to convert and save the mails found in this mailbox as .html files. :attr:`constance.get_config('DEFAULT_SAVE_TO_EML')` by default."""

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

    BASENAME = "mailbox"

    DELETE_NOTICE = _(
        "This will delete this mailbox and all emails and attachments found in it!"
    )

    class Meta:
        """Metadata class for the model."""

        db_table = "mailboxes"
        """The name of the database table for the mailboxes."""

        constraints: Final[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["name", "account"], name="mailbox_unique_together_name_account"
            )
        ]
        """:attr:`name` and :attr:`account` in combination are unique."""

    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the mailbox, using :attr:`name` and :attr:`account`.
        """
        return _("Mailbox %(name)s of %(account)s") % {
            "account": self.account,
            "name": self.name,
        }

    def getAvailableFetchingCriteria(self) -> list[str]:
        """Gets the available fetching criteria based on the mail protocol of this mailbox.

        Used by :func:`api.v1.views.MailboxViewSet.fetching_options` to show the choices for fetching to the user.

        Returns:
            list: A list of all available fetching criteria for this mailbox.

        Raises:
            ValueError: If the account has an unimplemented protocol.
        """
        return self.account.get_fetcher_class().AVAILABLE_FETCHING_CRITERIA

    def test_connection(self) -> None:
        """Tests whether the data in the model is correct.

        Tests connecting and logging in to the mailhost and account.
        The :attr:`core.models.MailboxModel.is_healthy` flag is set accordingly.
        Relies on the `test` method of the :mod:`core.utils.fetchers` classes.

        Raises:
            MailAccountError: If the test is fails due to an issue with the account.
            MailboxError: If the test is fails due to an issue with the mailbox.
        """

        logger.info("Testing %s ...", self)
        try:
            with self.account.get_fetcher() as fetcher:
                fetcher.test(self)
        except MailboxError as error:
            logger.info("Failed testing %s with error: %s.", self, error)
            self.is_healthy = False
            self.save(update_fields=["is_healthy"])
            raise
        except MailAccountError as error:
            logger.info("Failed testing %s with error %s.", self.account, error)
            self.account.is_healthy = False
            self.account.save(update_fields=["is_healthy"])
            raise
        self.is_healthy = True
        self.save(update_fields=["is_healthy"])
        logger.info("Successfully tested mailbox")

    def fetch(self, criterion: str) -> None:
        """Fetches emails from this mailbox based on :attr:`criterion` and adds them to the db.

        If successful, marks this mailbox as healthy, otherwise unhealthy.

        Args:
            criterion: The criterion used to fetch emails from the mailbox.

        Raises:
            MailboxError: If fetching failed.
        """
        logger.info("Fetching emails with criterion %s from %s ...", criterion, self)
        with self.account.get_fetcher() as fetcher:
            try:
                fetchedMails = fetcher.fetchEmails(self, criterion)
            except MailboxError:
                self.is_healthy = False
                self.save(update_fields=["is_healthy"])
                raise
        self.is_healthy = True
        self.save(update_fields=["is_healthy"])
        logger.info("Successfully fetched emails.")

        logger.info("Saving fetched emails ...")
        for fetchedMail in fetchedMails:
            EMailModel.createFromEmailBytes(fetchedMail, self)

        logger.info("Successfully saved fetched emails.")

    def addFromMailboxFile(self, file_data: bytes, file_format: str) -> None:
        """Adds emails from a mailbox file to the db.

        Supported formats are implemented via the :mod:`mailbox` package.

        Args:
            file_data: The bytes of the mailbox file.
            file_format: The format of the mailbox file. Case-insensitive.

        Raises:
            ValueError: If the file format is not implemented.
        """
        file_format = file_format.lower()
        logger.info("Adding emails from %s mailbox file to %s ...", file_format, self)
        if file_format == "mbox":
            formatClass: type[mailbox.Mailbox] = mailbox.mbox
        elif file_format == "mh":
            formatClass = mailbox.MH
        elif file_format == "babyl":
            formatClass = mailbox.Babyl
        elif file_format == "mmdf":
            formatClass = mailbox.MMDF
        elif file_format == "maildir":
            formatClass = mailbox.Maildir
        else:
            logger.info(
                "Failed adding emails from mailbox file to %s, format %s is not implemented.",
                file_format,
                self,
            )
            raise ValueError(f"Mailbox fileformat {file_format} is not implemented!")
        dump_filepath = os.path.join(
            get_config("TEMPORARY_STORAGE_DIRECTORY"), str(hash(file_data))
        )
        with open(dump_filepath, "bw") as file:
            file.write(file_data)
        mailboxFile = formatClass(dump_filepath)
        for key in mailboxFile.iterkeys():
            EMailModel.createFromEmailBytes(mailboxFile.get_bytes(key), self)
        logger.info("Successfully added emails from mailbox file.")

    @staticmethod
    def fromData(mailboxData: bytes, account: AccountModel) -> MailboxModel:
        """Prepares a :class:`core.models.MailboxModel.MailboxModel` from the mailboxname in bytes.

        Args:
            mailboxData: The bytes with the mailboxname.
            account: The account the mailbox is in.

        Returns:
            The :class:`core.models.MailboxModel.MailboxModel` instance with data from the bytes.
        """
        new_mailbox = MailboxModel(account=account)
        new_mailbox.name = parseMailboxName(mailboxData)
        return new_mailbox
