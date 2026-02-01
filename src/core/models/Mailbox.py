# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
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

import contextlib
import logging
import os
import re
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import TYPE_CHECKING, BinaryIO, ClassVar, override
from zipfile import BadZipFile, ZipFile

from dirtyfields import DirtyFieldsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin

from core.constants import (
    EmailFetchingCriterionChoices,
    MailboxTypeChoices,
    SupportedEmailDownloadFormats,
    SupportedEmailUploadFormats,
    file_format_parsers,
)
from core.mixins import (
    DownloadMixin,
    FavoriteModelMixin,
    HealthModelMixin,
    TimestampModelMixin,
    UploadMixin,
    URLMixin,
)
from core.utils.fetchers.exceptions import MailAccountError, MailboxError
from core.utils.mail_parsing import parse_mailbox_type
from eonvelope.utils.workarounds import get_config

from .Email import Email

if TYPE_CHECKING:
    from tempfile import _TemporaryFileWrapper

    from django_stubs_ext import StrOrPromise

    from .Account import Account


logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class Mailbox(
    ExportModelOperationsMixin("mailbox"),
    DirtyFieldsMixin,
    URLMixin,
    UploadMixin,
    DownloadMixin,
    FavoriteModelMixin,
    HealthModelMixin,
    TimestampModelMixin,
    models.Model,
):
    """Database model for a mailbox in a mail account."""

    BASENAME = "mailbox"

    DELETE_NOTICE = _(
        "This will delete the record of this mailbox and all emails and attachments found in it!"
    )

    DELETE_NOTICE_PLURAL = _(
        "This will delete the records of these mailboxes and all emails and attachments found in them!"
    )

    name = models.CharField(
        max_length=255,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("name"),
    )
    """The mailaccount internal name of the mailbox. Unique together with :attr:`account`."""

    type = models.CharField(
        default=MailboxTypeChoices.CUSTOM,
        choices=MailboxTypeChoices,
        max_length=32,
        verbose_name=_("type"),
    )
    """The mailaccount internal role or distinguished id of the mailbox."""

    account: models.ForeignKey[Account] = models.ForeignKey(
        "Account",
        related_name="mailboxes",
        on_delete=models.CASCADE,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("account"),
    )
    """The mailaccount this mailbox was found in. Unique together with :attr:`name`. Deletion of that `account` deletes this mailbox."""

    save_attachments = models.BooleanField(
        default=True,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("save attachments"),
        help_text=_(
            "Whether the attachments from the emails in this mailbox will be saved."
        ),
    )
    """Whether to save attachments of the mails found in this mailbox. :attr:`constance.get_config('DEFAULT_SAVE_ATTACHMENTS')` by default."""

    save_to_eml = models.BooleanField(
        default=True,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("save as .eml"),
        help_text=_("Whether the emails in this mailbox will be stored in .eml files."),
    )
    """Whether to save the mails found in this mailbox as .eml files. :attr:`constance.get_config('DEFAULT_SAVE_TO_EML')` by default."""

    class Meta:
        """Metadata class for the model."""

        db_table = "mailboxes"
        """The name of the database table for the mailboxes."""
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name = _("mailbox")
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name_plural = _("mailboxes")
        get_latest_by = TimestampModelMixin.Meta.get_latest_by

        constraints: ClassVar[list[models.BaseConstraint]] = [
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

    def test(self) -> None:
        """Tests whether the data in the model is correct.

        Tests connecting and logging in to the mailhost and account.
        The :attr:`core.models.Mailbox.is_healthy` flag is set accordingly.
        Relies on the `test` method of the :mod:`core.utils.fetchers` classes.

        Raises:
            MailAccountError: If the test is fails due to an issue with the account.
            MailboxError: If the test is fails due to an issue with the mailbox.
        """

        logger.info("Testing %s ...", self)
        with self.account.get_fetcher() as fetcher:
            try:
                fetcher.test(self)
            except MailboxError as error:
                logger.info("Failed testing %s with error: %s.", self, error)
                self.set_unhealthy(error)
                raise
            except MailAccountError as error:
                logger.info("Failed testing %s with error %s.", self.account, error)
                self.account.set_unhealthy(error)
                raise
        self.set_healthy()
        logger.info("Successfully tested mailbox")

    def fetch(self, criterion: str, criterion_arg: str) -> None:
        """Fetches emails from this mailbox based on :attr:`criterion` and adds them to the db.

        If successful, marks this mailbox as healthy, otherwise unhealthy.

        Args:
            criterion: The criterion used to fetch emails from the mailbox.
            criterion_arg: The argument for the criterion.

        Raises:
            MailboxError: Reraised if fetching failed due to a MailboxError.
            MailAccountError: Reraised if fetching failed due to a MailAccountError.
        """
        logger.info("Fetching emails with criterion %s from %s ...", criterion, self)
        with self.account.get_fetcher() as fetcher:
            try:
                fetched_mails = fetcher.fetch_emails(self, criterion, criterion_arg)
            except MailboxError as error:
                logger.info("Failed fetching %s with error: %s.", self, error)
                self.set_unhealthy(error)
                raise
            except MailAccountError as error:
                logger.info("Failed fetching %s with error: %s.", self, error)
                self.account.set_unhealthy(error)
                raise
        self.set_healthy()
        logger.info("Successfully fetched emails.")

        logger.info("Saving fetched emails ...")
        for fetched_mail in fetched_mails:
            Email.create_from_email_bytes(fetched_mail, self)

        logger.info("Successfully saved fetched emails.")

    def _add_email_from_eml(self, file: BinaryIO) -> None:
        """Reads emails from a zipped mailbox dir."""
        Email.create_from_email_bytes(file.read(), mailbox=self)

    def _add_emails_from_zip_eml(self, file: BinaryIO) -> None:
        """Reads emails from a zip of eml files."""
        try:
            with ZipFile(file) as zipfile:
                for zipped_file in zipfile.namelist():
                    Email.create_from_email_bytes(
                        zipfile.read(zipped_file), mailbox=self
                    )
        except BadZipFile as error:
            logger.exception("Error parsing file as zip!")
            raise ValueError(
                _("The given file is not a valid %(file_format)s.")
                % {"file_format": "zip"}
            ) from error

    def _add_emails_from_mailbox_file(self, file: BinaryIO, file_format: str) -> None:
        """Reads emails from a mailbox file.

        Note:
            Does not validate file_format! This has to be done beforehand.
        """
        parser_class = file_format_parsers[file_format]
        with NamedTemporaryFile() as tempfile:
            tempfile.write(file.read())
            tempfile.seek(0)
            parser = parser_class(tempfile.name, create=False)
            parser.lock()
            for key in parser.iterkeys():
                with contextlib.suppress(
                    AssertionError
                ):  # Babyl.get_bytes can raise AssertionError for a bad message
                    Email.create_from_email_bytes(parser.get_bytes(key), mailbox=self)
            parser.close()

    def _add_emails_from_mailbox_zip(self, file: BinaryIO, file_format: str) -> None:
        """Reads emails from a zipped mailbox dir.

        Note:
            Does not validate file_format! This has to be done beforehand.
        """
        parser_class = file_format_parsers[file_format]
        with TemporaryDirectory() as tempdirpath:
            try:
                with ZipFile(file) as zipfile:
                    zipfile.extractall(tempdirpath)
            except BadZipFile as error:
                logger.exception("Error parsing file as zip!")
                raise ValueError(
                    _("The given file is not a valid %(file_format)s.")
                    % {"file_format": "zip"}
                ) from error
            for name in os.listdir(tempdirpath):
                path = os.path.join(tempdirpath, name)
                if os.path.isdir(path):
                    parser = parser_class(path, create=False)
                    parser.lock()
                    try:
                        for key in parser.iterkeys():
                            Email.create_from_email_bytes(
                                parser.get_bytes(key), mailbox=self
                            )
                    except (
                        FileNotFoundError
                    ) as error:  # raised if the given maildir doesn't have the expected structure
                        logger.exception("Error parsing file as %s!", file_format)
                        raise ValueError(
                            _("The given file is not a valid %(file_format)s.")
                            % {"file_format": file_format}
                        ) from error
                    parser.close()

    def add_emails_from_file(self, file: BinaryIO, file_format: str) -> None:
        """Adds emails from a file to the db.

        Args:
            file: The mailbox file.
            file_format: The format of the mailbox file. Case-insensitive.

        Raises:
            ValueError: If the file format is not implemented or the file failed to open.
        """
        file_format = file_format.lower()
        logger.info("Adding emails from %s file to %s ...", file_format, self)
        match file_format:
            case SupportedEmailUploadFormats.EML:
                self._add_email_from_eml(file)
            case SupportedEmailUploadFormats.ZIP_EML:
                self._add_emails_from_zip_eml(file)
            case (
                SupportedEmailUploadFormats.MBOX
                | SupportedEmailUploadFormats.MMDF
                | SupportedEmailUploadFormats.BABYL
            ):
                self._add_emails_from_mailbox_file(file, file_format)
            case SupportedEmailUploadFormats.MAILDIR | SupportedEmailUploadFormats.MH:
                self._add_emails_from_mailbox_zip(file, file_format)
            case _:
                logger.error("Unsupported fileformat for uploaded file.")
                raise ValueError(
                    _("The file format %(file_format)s is not supported.")
                    % {"file_format": file_format}
                )
        logger.info("Successfully added emails from file.")

    @property
    @override
    def has_download(self) -> bool:
        return self.emails.exists()

    @property
    def available_fetching_criteria(self) -> tuple[StrOrPromise]:
        """Gets the available fetching criteria based on the mail protocol of this mailbox.

        Returns:
            A tuple of all available fetching criteria for this mailbox.

        Raises:
            ValueError: If the account has an unimplemented protocol.
        """
        return self.account.get_fetcher_class().AVAILABLE_FETCHING_CRITERIA  # type: ignore[no-any-return]  # for some reason mypy doesn't get this

    @property
    def available_no_arg_fetching_criteria(self) -> tuple[StrOrPromise]:
        """Gets the available fetching criteria that do not require an argument based on the mail protocol of this mailbox.

        Returns:
            A tuple of all available fetching criteria that do not require an argument for this mailbox.

        Raises:
            ValueError: If the account has an unimplemented protocol.
        """
        return tuple(
            criterion
            for criterion in self.available_fetching_criteria
            if criterion.format("arg") == criterion
        )  # type: ignore[no-any-return]  # for some reason mypy doesn't get this

    @property
    def available_fetching_criterion_choices(self) -> list[tuple[str, StrOrPromise]]:
        """Gets the available fetching criterion choices based on the mail protocol of this mailbox.

        Returns:
            A choices-type tuple of all available fetching criteria for this mailbox.

        Raises:
            ValueError: If the account has an unimplemented protocol.
        """
        return [
            (criterion, label)
            for criterion, label in EmailFetchingCriterionChoices.choices
            if criterion in self.account.get_fetcher_class().AVAILABLE_FETCHING_CRITERIA
        ]

    @property
    def available_no_arg_fetching_criterion_choices(
        self,
    ) -> list[tuple[str, StrOrPromise]]:
        """Gets the available fetching criterion choices that do not require an argumentbased on the mail protocol of this mailbox.

        Returns:
            A choices-type tuple of all available fetching criteria that do not require an argument for this mailbox.

        Raises:
            ValueError: If the account has an unimplemented protocol.
        """
        return [
            (criterion, label)
            for criterion, label in self.available_fetching_criterion_choices
            if criterion.format("arg") == criterion
        ]

    @property
    def available_download_formats(self) -> list[tuple[str, StrOrPromise]]:
        """Get all formats that emails in this mailbox can be downloaded in.

        Returns:
            A list of download formats and format names.
        """
        return SupportedEmailDownloadFormats.choices

    @classmethod
    def create_from_data(
        cls, mailbox_name: str, mailbox_type: str, account: Account
    ) -> Mailbox | None:
        """Creates a :class:`core.models.Mailbox` from the mailboxdata.

        Note:
            Mailbox created from data is considered healthy by default.

        Args:
            mailbox_name: The name of the mailbox.
            mailbox_type: The type of the mailbox.
            account: The account the mailbox is in.

        Returns:
            The :class:`core.models.Mailbox` instance with data from the bytes.
            `None` if the mailbox name is ignored.

        Raises:
            Account.DoesNotExist: If the given account is not in the db.
        """
        if account.pk is None:
            raise ValueError("Account is not in the db!")
        mailbox_type = parse_mailbox_type(mailbox_type)
        if get_config("THROW_OUT_SPAM") and (mailbox_type == MailboxTypeChoices.JUNK):
            logger.debug("%s is a spambox, it is skipped.", mailbox_name)
            return None
        if re.compile(
            get_config("IGNORED_MAILBOXES_REGEX"), flags=re.IGNORECASE
        ).search(mailbox_name):
            logger.debug("%s is in the ignorelist, it is skipped.", mailbox_name)
            return None
        try:
            mailbox = cls.objects.get(account=account, name=mailbox_name)
            mailbox.type = mailbox_type  # for migration of old mailbox instances
            mailbox.save(update_fields=["type"])
            mailbox.set_healthy()
            logger.debug(
                "%s already exists in db, it has been set to healthy.", mailbox
            )
        except Mailbox.DoesNotExist:
            mailbox = cls(
                account=account,
                name=mailbox_name,
                type=mailbox_type,
                save_to_eml=get_config("DEFAULT_SAVE_TO_EML"),
                save_attachments=get_config("DEFAULT_SAVE_ATTACHMENTS"),
                is_healthy=True,
            )
            mailbox.save()
            logger.debug("Successfully saved %s to db.", mailbox_name)
        return mailbox

    @staticmethod
    def queryset_as_file(
        queryset: models.QuerySet[Mailbox], file_format: str
    ) -> _TemporaryFileWrapper:
        """Processes the files of the emails in the mailboxes in the queryset into a temporary file.

        Args:
            queryset: The mailbox queryset to compile into a file.
            file_format: The desired format of the mailbox files. Must be one of :class:`core.constants.SupportedEmailDownloadFormats`. Case-insensitive.

        Returns:
            The temporary file wrapper.

        Raises:
            ValueError: If the given :attr:`file_format` is not supported.
            Mailbox.DoesNotExist: If the :attr:`queryset` is empty.
        """
        if not queryset.exists():
            raise Mailbox.DoesNotExist("The queryset is empty")

        file_format = file_format.lower()
        tempfile = (
            NamedTemporaryFile()  # noqa: SIM115  # pylint: disable=consider-using-with
        )  # the file must not be closed as it is returned later
        with ZipFile(tempfile.name, "w") as zipfile:
            for mailbox in queryset:
                try:
                    mailbox_file = Email.queryset_as_file(
                        mailbox.emails.all(), file_format
                    )
                except Email.DoesNotExist:
                    continue
                with (
                    mailbox_file,
                    zipfile.open(
                        mailbox.name + "." + file_format.split("[", maxsplit=1)[0], "w"
                    ) as zipped_file,
                ):
                    zipped_file.write(mailbox_file.read())
        return tempfile
