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

"""Module with the :class:`Mailbox` model class."""

from __future__ import annotations

import logging
import mailbox
import os
from typing import TYPE_CHECKING, Final, override

from dirtyfields import DirtyFieldsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from Emailkasten.utils.workarounds import get_config

from ..mixins.FavoriteMixin import FavoriteMixin
from ..mixins.UploadMixin import UploadMixin
from ..mixins.URLMixin import URLMixin
from ..utils.fetchers.exceptions import MailAccountError, MailboxError
from ..utils.mail_parsing import parse_mailbox_name
from .Email import Email


if TYPE_CHECKING:
    from .Account import Account


logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class Mailbox(DirtyFieldsMixin, URLMixin, UploadMixin, FavoriteMixin, models.Model):
    """Database model for a mailbox in a mail account."""

    name = models.CharField(max_length=255)
    """The mailaccount internal name of the mailbox. Unique together with :attr:`account`."""

    account: models.ForeignKey[Account] = models.ForeignKey(
        "Account", related_name="mailboxes", on_delete=models.CASCADE
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

    save_to_eml = models.BooleanField(
        default=get_config("DEFAULT_SAVE_TO_EML"),
        verbose_name=_("Save as .eml"),
        help_text=_("Whether the emails in this mailbox will be stored in .eml files."),
    )
    """Whether to save the mails found in this mailbox as .eml files. :attr:`constance.get_config('DEFAULT_SAVE_TO_EML')` by default."""

    save_to_html = models.BooleanField(
        default=get_config("DEFAULT_SAVE_TO_HTML"),
        verbose_name=_("Save as .html"),
        help_text=_(
            "Whether the emails in this mailbox will be converted and stored in .html files."
        ),
    )
    """Whether to convert and save the mails found in this mailbox as .html files. :attr:`constance.get_config('DEFAULT_SAVE_TO_EML')` by default."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite mailboxes. False by default."""

    is_healthy = models.BooleanField(null=True)
    """Flags whether the mailbox can be accessed and read. `None` by default.
    When the :attr:`core.models.Account.is_healthy` field changes to `False`, this field is updated accordingly.
    When this field changes to `True`, the :attr:`core.models.Account.is_healthy` field of :attr:`account` will be set to `True` as well by a signal."""

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

    @override
    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the mailbox, using :attr:`name` and :attr:`account`.
        """
        return _("Mailbox %(name)s of %(account)s") % {
            "account": self.account,
            "name": self.name,
        }

    def get_available_fetching_criteria(self) -> list[str]:
        """Gets the available fetching criteria based on the mail protocol of this mailbox.

        Used by :func:`api.v1.views.MailboxViewSet.fetching_options` to show the choices for fetching to the user.

        Returns:
            list: A list of all available fetching criteria for this mailbox.

        Raises:
            ValueError: If the account has an unimplemented protocol.
        """
        return self.account.get_fetcher_class().AVAILABLE_FETCHING_CRITERIA  # type: ignore[no-any-return]  # for some reason mypy doesnt get this

    def test_connection(self) -> None:
        """Tests whether the data in the model is correct.

        Tests connecting and logging in to the mailhost and account.
        The :attr:`core.models.Mailbox.is_healthy` flag is set accordingly.
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
                fetched_mails = fetcher.fetch_emails(self, criterion)
            except MailboxError:
                self.is_healthy = False
                self.save(update_fields=["is_healthy"])
                raise
        self.is_healthy = True
        self.save(update_fields=["is_healthy"])
        logger.info("Successfully fetched emails.")

        logger.info("Saving fetched emails ...")
        for fetched_mail in fetched_mails:
            Email.create_from_email_bytes(fetched_mail, self)

        logger.info("Successfully saved fetched emails.")

    def add_from_mailbox_file(self, file_data: bytes, file_format: str) -> None:
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
            format_class: type[mailbox.Mailbox] = mailbox.mbox
        elif file_format == "mh":
            format_class = mailbox.MH
        elif file_format == "babyl":
            format_class = mailbox.Babyl
        elif file_format == "mmdf":
            format_class = mailbox.MMDF
        elif file_format == "maildir":
            format_class = mailbox.Maildir
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
        mailbox_file = format_class(dump_filepath)  # type: ignore[abstract]  # Mailbox class is never implemented, it's just used for typing
        for key in mailbox_file.iterkeys():
            Email.create_from_email_bytes(mailbox_file.get_bytes(key), self)
        logger.info("Successfully added emails from mailbox file.")

    @classmethod
    def create_from_data(cls, mailbox_data: bytes, account: Account) -> Mailbox:
        """Creates a :class:`core.models.Mailbox` from the mailboxname in bytes.

        Args:
            mailbox_data: The bytes with the mailboxname.
            account: The account the mailbox is in.

        Returns:
            The :class:`core.models.Mailbox` instance with data from the bytes.
            `None` if the mailbox already exists in the db.
        """
        if account.pk is None:
            raise ValueError("Account is not in the db!")
        mailbox_name = parse_mailbox_name(mailbox_data)
        try:
            new_mailbox = cls.objects.get(account=account, name=mailbox_name)
            logger.debug("%s already exists in db, it is skipped!", new_mailbox)
        except Mailbox.DoesNotExist:
            new_mailbox = cls(account=account, name=mailbox_name)
            new_mailbox.save()
            logger.debug("Successfully saved mailbox to db!")
        return new_mailbox
