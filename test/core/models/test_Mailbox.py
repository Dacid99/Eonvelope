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

"""Test module for :mod:`core.models.Mailbox`."""

from __future__ import annotations

import datetime
import mailbox
import os
import re
import shutil
import tempfile
from io import BytesIO
from tempfile import NamedTemporaryFile, TemporaryDirectory, gettempdir
from zipfile import ZipFile

import pytest
from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.urls import reverse
from model_bakery import baker
from pyfakefs.fake_filesystem_unittest import Pause

from core.constants import (
    EmailFetchingCriterionChoices,
    MailboxTypeChoices,
    SupportedEmailDownloadFormats,
    SupportedEmailUploadFormats,
    file_format_parsers,
)
from core.models import Account, Mailbox
from core.utils.fetchers import (
    ExchangeFetcher,
    IMAP4_SSL_Fetcher,
    IMAP4Fetcher,
    JMAPFetcher,
    POP3_SSL_Fetcher,
    POP3Fetcher,
)
from core.utils.fetchers.exceptions import MailAccountError, MailboxError
from eonvelope.utils.workarounds import get_config
from test.conftest import TEST_EMAIL_PARAMETERS

from .test_Account import mock_Account_get_fetcher, mock_fetcher


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """The mocked :attr:`core.models.Mailbox.logger`."""
    return mocker.patch("core.models.Mailbox.logger", autospec=True)


@pytest.fixture
def mock_Email_create_from_email_bytes(mocker):
    """Patches `core.models.Email.create_from_email_bytes`."""
    return mocker.patch(
        "core.models.Email.Email.create_from_email_bytes", autospec=True
    )


@pytest.mark.django_db
def test_Mailbox_fields(fake_mailbox):
    """Tests the fields of :class:`core.models.Mailbox.Mailbox`."""

    assert fake_mailbox.name is not None
    assert fake_mailbox.type is not None
    assert fake_mailbox.type == MailboxTypeChoices.CUSTOM
    assert fake_mailbox.account is not None
    assert isinstance(fake_mailbox.account, Account)
    assert fake_mailbox.save_attachments is True
    assert fake_mailbox.save_to_eml is True
    assert fake_mailbox.is_favorite is False
    assert fake_mailbox.is_healthy is None
    assert isinstance(fake_mailbox.updated, datetime.datetime)
    assert fake_mailbox.updated is not None
    assert isinstance(fake_mailbox.created, datetime.datetime)
    assert fake_mailbox.created is not None


@pytest.mark.django_db
def test_Mailbox___str__(fake_mailbox):
    """Tests the string representation of :class:`core.models.Mailbox.Mailbox`."""
    assert fake_mailbox.name in str(fake_mailbox)
    assert str(fake_mailbox.account) in str(fake_mailbox)


@pytest.mark.django_db
def test_Mailbox_foreign_key_deletion(fake_mailbox):
    """Tests the on_delete foreign key constraint in :class:`core.models.Mailbox.Mailbox`."""

    assert fake_mailbox is not None
    fake_mailbox.account.delete()
    with pytest.raises(Mailbox.DoesNotExist):
        fake_mailbox.refresh_from_db()


@pytest.mark.django_db
def test_Mailbox_unique_constraints(mocker, fake_account):
    """Tests the unique constraints of :class:`core.models.Mailbox.Mailbox`."""
    mocker.patch("core.models.Account.Account.update_mailboxes")

    mailbox_1 = baker.make(Mailbox, name="abc123")
    mailbox_2 = baker.make(Mailbox, name="abc123")
    assert mailbox_1.name == mailbox_2.name
    assert mailbox_1.account != mailbox_2.account

    mailbox_1 = baker.make(Mailbox, account=fake_account)
    mailbox_2 = baker.make(Mailbox, account=fake_account)
    assert mailbox_1.name != mailbox_2.name
    assert mailbox_1.account == mailbox_2.account

    baker.make(Mailbox, name="abc123", account=fake_account)
    with pytest.raises(IntegrityError):
        baker.make(Mailbox, name="abc123", account=fake_account)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "protocol, expected_fetching_criteria",
    [
        (ExchangeFetcher.PROTOCOL, ExchangeFetcher.AVAILABLE_FETCHING_CRITERIA),
        (IMAP4Fetcher.PROTOCOL, IMAP4Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (POP3Fetcher.PROTOCOL, POP3Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (IMAP4_SSL_Fetcher.PROTOCOL, IMAP4_SSL_Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (POP3_SSL_Fetcher.PROTOCOL, POP3_SSL_Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (JMAPFetcher.PROTOCOL, JMAPFetcher.AVAILABLE_FETCHING_CRITERIA),
    ],
)
def test_Mailbox_available_fetching_criteria(
    fake_mailbox, protocol, expected_fetching_criteria
):
    """Tests :func:`core.models.Mailbox.Mailbox.available_fetching_criteria`."""

    fake_mailbox.account.protocol = protocol

    result = fake_mailbox.available_fetching_criteria

    assert result == expected_fetching_criteria


@pytest.mark.django_db
@pytest.mark.parametrize(
    "protocol, expected_fetching_criteria",
    [
        (ExchangeFetcher.PROTOCOL, ExchangeFetcher.AVAILABLE_FETCHING_CRITERIA),
        (IMAP4Fetcher.PROTOCOL, IMAP4Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (POP3Fetcher.PROTOCOL, POP3Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (IMAP4_SSL_Fetcher.PROTOCOL, IMAP4_SSL_Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (POP3_SSL_Fetcher.PROTOCOL, POP3_SSL_Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (JMAPFetcher.PROTOCOL, JMAPFetcher.AVAILABLE_FETCHING_CRITERIA),
    ],
)
def test_Mailbox_available__no_arg_fetching_criteria(
    fake_mailbox, protocol, expected_fetching_criteria
):
    """Tests :func:`core.models.Mailbox.Mailbox.available_fetching_criteria`."""

    fake_mailbox.account.protocol = protocol

    result = fake_mailbox.available_no_arg_fetching_criteria

    assert result == tuple(
        criterion
        for criterion in expected_fetching_criteria
        if criterion.format("test") == criterion
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "protocol, expected_fetching_criteria",
    [
        (ExchangeFetcher.PROTOCOL, ExchangeFetcher.AVAILABLE_FETCHING_CRITERIA),
        (IMAP4Fetcher.PROTOCOL, IMAP4Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (POP3Fetcher.PROTOCOL, POP3Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (IMAP4_SSL_Fetcher.PROTOCOL, IMAP4_SSL_Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (POP3_SSL_Fetcher.PROTOCOL, POP3_SSL_Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (JMAPFetcher.PROTOCOL, JMAPFetcher.AVAILABLE_FETCHING_CRITERIA),
    ],
)
def test_Mailbox_available_fetching_criterion_choices(
    fake_mailbox, protocol, expected_fetching_criteria
):
    """Tests :func:`core.models.Mailbox.Mailbox.available_fetching_criteria`."""

    fake_mailbox.account.protocol = protocol

    result = fake_mailbox.available_fetching_criterion_choices

    assert result == [
        (criterion, label)
        for criterion, label in EmailFetchingCriterionChoices.choices
        if criterion in expected_fetching_criteria
    ]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "protocol, expected_fetching_criteria",
    [
        (ExchangeFetcher.PROTOCOL, ExchangeFetcher.AVAILABLE_FETCHING_CRITERIA),
        (IMAP4Fetcher.PROTOCOL, IMAP4Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (POP3Fetcher.PROTOCOL, POP3Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (IMAP4_SSL_Fetcher.PROTOCOL, IMAP4_SSL_Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (POP3_SSL_Fetcher.PROTOCOL, POP3_SSL_Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (JMAPFetcher.PROTOCOL, JMAPFetcher.AVAILABLE_FETCHING_CRITERIA),
    ],
)
def test_Mailbox_available__no_arg_fetching_criterion_choices(
    fake_mailbox, protocol, expected_fetching_criteria
):
    """Tests :func:`core.models.Mailbox.Mailbox.available_no_arg_fetching_criteria`."""

    fake_mailbox.account.protocol = protocol

    result = fake_mailbox.available_no_arg_fetching_criterion_choices

    assert result == [
        (criterion, label)
        for criterion, label in EmailFetchingCriterionChoices.choices
        if criterion in expected_fetching_criteria
        and (criterion.format("test") == criterion)
    ]


@pytest.mark.django_db
def test_Mailbox_test__success(
    fake_mailbox, mock_logger, mock_fetcher, mock_Account_get_fetcher
):
    """Tests :func:`core.models.Mailbox.Mailbox.test`
    in case of success.
    """
    fake_mailbox.is_healthy = False
    fake_mailbox.save(update_fields=["is_healthy"])

    fake_mailbox.test()

    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_healthy is True
    mock_Account_get_fetcher.assert_called_once_with(fake_mailbox.account)
    mock_fetcher.test.assert_called_once_with(fake_mailbox)
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_Mailbox_test__bad_protocol(
    fake_mailbox, mock_logger, mock_Account_get_fetcher, mock_fetcher
):
    """Tests :func:`core.models.Mailbox.Mailbox.test`
    in case the account of the mailbox has a bad :attr:`core.models.Account.Account.protocol` field
    and thus get_fetcher raises a :class:`ValueError`.
    """
    mock_Account_get_fetcher.side_effect = ValueError("Bad protocol OTHER")

    with pytest.raises(
        ValueError, check=lambda error: error == mock_Account_get_fetcher.side_effect
    ):
        fake_mailbox.test()

    mock_Account_get_fetcher.assert_called_once_with(fake_mailbox.account)
    mock_fetcher.test.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("test_side_effect", [MailboxError, MailAccountError])
def test_Mailbox_test__failure(
    fake_mailbox,
    mock_logger,
    mock_Account_get_fetcher,
    mock_fetcher,
    test_side_effect,
):
    """Tests :func:`core.models.Mailbox.Mailbox.test`
    in case the test fails with a :class:`core.utils.fetchers.exceptions.FetcherError`.
    """
    mock_fetcher.test.side_effect = test_side_effect(Exception())
    fake_mailbox.is_healthy = True
    fake_mailbox.save(update_fields=["is_healthy"])

    with pytest.raises(test_side_effect):
        fake_mailbox.test()

    if test_side_effect == MailboxError:
        assert fake_mailbox.is_healthy is False
    elif test_side_effect == MailAccountError:
        assert fake_mailbox.account.is_healthy is False
    mock_Account_get_fetcher.assert_called_once_with(fake_mailbox.account)
    mock_fetcher.test.assert_called_once_with(fake_mailbox)
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_Mailbox_test__get_fetcher_error(
    fake_mailbox, mock_logger, mock_Account_get_fetcher, mock_fetcher
):
    """Tests :func:`core.models.Mailbox.Mailbox.test`
    in case :func:`core.models.Account.Account.get_fetcher`
    raises a :class:`core.utils.fetchers.exceptions.MailAccountError`.
    In that case the account should not be flagged, as that is already done in get_fetcher itself.
    """
    mock_Account_get_fetcher.side_effect = MailAccountError(Exception())
    fake_mailbox.is_healthy = True
    fake_mailbox.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        fake_mailbox.test()

    assert fake_mailbox.account.is_healthy is True
    mock_Account_get_fetcher.assert_called_once_with(fake_mailbox.account)
    mock_fetcher.test.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_Mailbox_fetch__success(
    faker,
    fake_mailbox,
    mock_logger,
    mock_Account_get_fetcher,
    mock_fetcher,
    mock_Email_create_from_email_bytes,
):
    """Tests :func:`core.models.Mailbox.Mailbox.fetch`
    in case of success.
    """
    fake_criterion = faker.word()
    fake_criterion_arg = faker.word()
    fake_mailbox.is_healthy = False
    fake_mailbox.save(update_fields=["is_healthy"])

    fake_mailbox.fetch(fake_criterion, fake_criterion_arg)

    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_healthy is True
    mock_Account_get_fetcher.assert_called_once_with(fake_mailbox.account)
    mock_fetcher.fetch_emails.assert_called_once_with(
        fake_mailbox, fake_criterion, fake_criterion_arg
    )
    assert mock_Email_create_from_email_bytes.call_count == len(
        mock_fetcher.fetch_emails.return_value
    )
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_Mailbox_fetch__failure(
    faker,
    fake_mailbox,
    mock_logger,
    mock_fetcher,
    mock_Account_get_fetcher,
    mock_Email_create_from_email_bytes,
):
    """Tests :func:`core.models.Mailbox.Mailbox.fetch`
    in case fetching fails with a :class:`core.utils.fetchers.exceptions.MailboxError`.
    """
    fake_criterion = faker.word()
    fake_criterion_arg = faker.word()
    mock_fetcher.fetch_emails.side_effect = MailboxError(Exception())
    fake_mailbox.is_healthy = True
    fake_mailbox.save(update_fields=["is_healthy"])

    with pytest.raises(MailboxError):
        fake_mailbox.fetch(fake_criterion, fake_criterion_arg)

    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_healthy is False
    mock_Account_get_fetcher.assert_called_once_with(fake_mailbox.account)
    mock_fetcher.fetch_emails.assert_called_once_with(
        fake_mailbox, fake_criterion, fake_criterion_arg
    )
    mock_Email_create_from_email_bytes.assert_not_called()
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_Mailbox_fetch__get_fetcher_error(
    fake_mailbox,
    mock_logger,
    mock_Account_get_fetcher,
    mock_fetcher,
    mock_Email_create_from_email_bytes,
):
    """Tests :func:`core.models.Mailbox.Mailbox.fetch`
    in case :func:`core.models.Account.Account.get_fetcher`
    raises a :class:`core.utils.fetchers.exceptions.MailAccountError`.
    """
    mock_Account_get_fetcher.side_effect = MailAccountError(Exception())
    fake_mailbox.is_healthy = True
    fake_mailbox.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        fake_mailbox.fetch("criterion", "value")

    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_healthy is True
    mock_Account_get_fetcher.assert_called_once_with(fake_mailbox.account)
    mock_fetcher.fetch_emails.assert_not_called()
    mock_Email_create_from_email_bytes.assert_not_called()
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_format",
    [SupportedEmailUploadFormats.EML, SupportedEmailUploadFormats.EML.title()],
)
def test_Mailbox_add_emails_from_file_eml__success(
    fake_fs, fake_mailbox, mock_logger, file_format
):
    """Tests :func:`core.models.Account.Account.add_emails_from_file`
    in case of .
    """
    with Pause(fake_fs), open(TEST_EMAIL_PARAMETERS[0][0], "rb") as test_email:
        eml_data = test_email.read()

    assert fake_mailbox.emails.count() == 0

    fake_mailbox.add_emails_from_file(BytesIO(eml_data), file_format)

    assert fake_mailbox.emails.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_format",
    [SupportedEmailUploadFormats.ZIP_EML, SupportedEmailUploadFormats.ZIP_EML.title()],
)
def test_Mailbox_add_emails_from_file_zip_eml__success(
    fake_fs, fake_mailbox, mock_logger, file_format
):
    """Tests :func:`core.models.Account.Account.add_emails_from_file`
    in case of .
    """
    with NamedTemporaryFile() as tempfile:
        with ZipFile(tempfile, "w") as zipfile:
            for index in (0, 1, 2):
                with zipfile.open(f"{index}.eml", "w") as zipped_file:
                    with (
                        Pause(fake_fs),
                        open(TEST_EMAIL_PARAMETERS[index][0], "rb") as test_email,
                    ):
                        test_email_bytes = test_email.read()
                    zipped_file.write(test_email_bytes)
            assert len(zipfile.namelist()) == 3
        assert fake_mailbox.emails.count() == 0

        fake_mailbox.add_emails_from_file(tempfile, file_format)

    assert fake_mailbox.emails.count() == 3
    for index in (0, 1, 2):
        assert fake_mailbox.emails.filter(
            message_id=TEST_EMAIL_PARAMETERS[index][1]["message_id"]
        ).exists()

    assert os.listdir(gettempdir()) == []


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_format",
    [SupportedEmailUploadFormats.ZIP_EML, SupportedEmailUploadFormats.ZIP_EML.title()],
)
def test_Mailbox_add_emails_from_file__zip_eml__bad_file(
    faker,
    fake_fs,
    fake_mailbox,
    mock_logger,
    file_format,
):
    """Tests :func:`core.models.Account.Account.add_emails_from_file`
    in case of a bad zip of eml.
    """
    assert fake_mailbox.emails.count() == 0

    with pytest.raises(ValueError, match=re.compile("zip", re.IGNORECASE)):
        fake_mailbox.add_emails_from_file(BytesIO(faker.text().encode()), file_format)

    assert fake_mailbox.emails.count() == 0
    assert os.listdir(gettempdir()) == []
    mock_logger.exception.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_format",
    [
        SupportedEmailUploadFormats.MBOX,
        SupportedEmailUploadFormats.MMDF,
        SupportedEmailUploadFormats.BABYL,
        SupportedEmailUploadFormats.MBOX.title(),
        SupportedEmailUploadFormats.MMDF.title(),
        SupportedEmailUploadFormats.BABYL.title(),
    ],
)
def test_Mailbox_add_emails_from_file__mailbox_file__success(
    fake_fs, fake_mailbox, mock_logger, file_format
):
    """Tests :func:`core.models.Account.Account.add_emails_from_file`
    in case of success.
    """
    parser_class = file_format_parsers[file_format.lower()]
    with NamedTemporaryFile() as tempfile:
        parser = parser_class(tempfile.name, create=True)
        parser.lock()
        for index in (0, 1, 2):
            with (
                Pause(fake_fs),
                open(TEST_EMAIL_PARAMETERS[index][0], "rb") as test_email,
            ):
                parser.add(test_email.read())
        assert len(list(parser.iterkeys())) == 3
        parser.close()

        assert fake_mailbox.emails.count() == 0

        fake_mailbox.add_emails_from_file(tempfile, file_format)

    assert fake_mailbox.emails.count() == 3
    for index in (0, 1, 2):
        assert fake_mailbox.emails.filter(
            message_id=TEST_EMAIL_PARAMETERS[index][1]["message_id"]
        ).exists()
    assert os.listdir(gettempdir()) == []
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()
    mock_logger.exception.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_format",
    [
        SupportedEmailUploadFormats.MBOX,
        SupportedEmailUploadFormats.MMDF,
        SupportedEmailUploadFormats.BABYL,
    ],
)
def test_Mailbox_add_emails_from_file__mailbox_file__bad_file(
    faker,
    fake_fs,
    fake_mailbox,
    mock_logger,
    file_format,
):
    """Tests :func:`core.models.Account.Account.add_emails_from_file`
    in case of success.
    """
    assert fake_mailbox.emails.count() == 0

    fake_mailbox.add_emails_from_file(BytesIO(faker.text().encode()), file_format)

    assert fake_mailbox.emails.count() == 0
    assert os.listdir(gettempdir()) == []
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()
    mock_logger.exception.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_format",
    [
        SupportedEmailUploadFormats.MAILDIR,
        SupportedEmailUploadFormats.MH,
        SupportedEmailUploadFormats.MAILDIR.title(),
        SupportedEmailUploadFormats.MH.title(),
    ],
)
def test_Mailbox_add_emails_from_file__mailbox_dir__success(
    fake_fs, fake_mailbox, mock_logger, file_format
):
    """Tests :func:`core.models.Account.Account.add_emails_from_file`
    in case of success.
    """
    parser_class = file_format_parsers[file_format.lower()]
    with TemporaryDirectory() as tempdirpath:
        parser = parser_class(os.path.join(tempdirpath, "test"), create=True)
        parser.lock()
        for index in (0, 1, 2):
            with (
                Pause(fake_fs),
                open(TEST_EMAIL_PARAMETERS[index][0], "rb") as test_email,
            ):
                test_email_bytes = test_email.read()
            parser.add(test_email_bytes)
        assert len(list(parser.iterkeys())) == 3
        parser.close()
        with NamedTemporaryFile(suffix=".zip") as tempfile:
            shutil.make_archive(os.path.splitext(tempfile.name)[0], "zip", tempdirpath)

            assert fake_mailbox.emails.count() == 0

            fake_mailbox.add_emails_from_file(tempfile, file_format)

    assert fake_mailbox.emails.count() == 3
    for index in (0, 1, 2):
        assert fake_mailbox.emails.filter(
            message_id=TEST_EMAIL_PARAMETERS[index][1]["message_id"]
        ).exists()
    assert os.listdir(gettempdir()) == []
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()
    mock_logger.exception.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_format",
    [
        SupportedEmailUploadFormats.MAILDIR,
        SupportedEmailUploadFormats.MH,
    ],
)
def test_Mailbox_add_emails_from_file__mailbox_dir__bad_zip(
    faker, fake_fs, fake_mailbox, mock_logger, file_format
):
    """Tests :func:`core.models.Account.Account.add_emails_from_file`
    in case of bad zip of mailbox directory.
    """
    assert fake_mailbox.emails.count() == 0

    with pytest.raises(ValueError, match=re.compile("zip", re.IGNORECASE)):
        fake_mailbox.add_emails_from_file(BytesIO(faker.text().encode()), file_format)

    assert fake_mailbox.emails.count() == 0
    assert os.listdir(gettempdir()) == []
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_Mailbox_add_emails_from_file__mailbox_dir__bad_maildir(
    fake_fs, fake_mailbox, mock_logger
):
    """Tests :func:`core.models.Account.Account.add_emails_from_file`
    in case of a bad maildir in the zip.
    """
    with TemporaryDirectory() as tempdirpath:
        parser = mailbox.Maildir(tempdirpath, create=True)
        os.makedirs(os.path.join(tempdirpath, "new"))
        os.makedirs(os.path.join(tempdirpath, "tmp"))
        parser.lock()
        with Pause(fake_fs), open(TEST_EMAIL_PARAMETERS[0][0], "rb") as test_email:
            test_email_bytes = test_email.read()
        parser.add(test_email_bytes)
        parser.close()
        with NamedTemporaryFile(suffix=".zip") as tempfile:
            shutil.make_archive(os.path.splitext(tempfile.name)[0], "zip", tempdirpath)

            assert fake_mailbox.emails.count() == 0

            with pytest.raises(
                ValueError, match=re.escape(SupportedEmailUploadFormats.MAILDIR.lower())
            ):
                fake_mailbox.add_emails_from_file(
                    tempfile, SupportedEmailUploadFormats.MAILDIR
                )

    assert fake_mailbox.emails.count() == 0
    assert os.listdir(gettempdir()) == []
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_Mailbox_add_emails_from_file__mailbox_dir__bad_mh(
    fake_fs, fake_mailbox, mock_logger
):
    """Tests :func:`core.models.Account.Account.add_emails_from_file`
    in case of a bad mh in the zip.
    """
    with TemporaryDirectory() as tempdirpath:
        parser = mailbox.MH(tempdirpath, create=True)
        parser.lock()
        with Pause(fake_fs), open(TEST_EMAIL_PARAMETERS[0][0], "rb") as test_email:
            test_email_bytes = test_email.read()
        parser.add(test_email_bytes)
        parser.close()
        with NamedTemporaryFile(suffix=".zip") as tempfile:
            shutil.make_archive(os.path.splitext(tempfile.name)[0], "zip", tempdirpath)

            assert fake_mailbox.emails.count() == 0

            fake_mailbox.add_emails_from_file(tempfile, SupportedEmailUploadFormats.MH)

    assert fake_mailbox.emails.count() == 0
    assert os.listdir(gettempdir()) == []
    mock_logger.exception.assert_not_called()


@pytest.mark.django_db
def test_Mailbox_add_emails_from_file__bad_format(
    fake_fs, fake_file, fake_mailbox, mock_logger
):
    """Tests :func:`core.models.Account.Account.add_emails_from_file`
    in case of the mailbox file format is an unsupported format.
    """
    with pytest.raises(ValueError, match=re.compile("format", re.IGNORECASE)):
        fake_mailbox.add_emails_from_file(fake_file, "unimPLemented")

    assert os.listdir(gettempdir()) == []
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_Mailbox_queryset_as_file_zip_eml(
    fake_file, fake_mailbox, fake_email, fake_email_with_file
):
    """Tests :func:`core.models.Mailbox.Mailbox.queryset_as_file`
    in case the requested format is zip of eml.
    """
    assert Mailbox.objects.count() == 1
    assert fake_mailbox.emails.count() == 2

    result = Mailbox.queryset_as_file(
        Mailbox.objects.all(), SupportedEmailDownloadFormats.ZIP_EML
    )

    assert Mailbox.objects.count() == 1
    assert hasattr(result, "read")
    with ZipFile(result) as zipfile:
        assert fake_mailbox.name in zipfile.namelist()
        with (
            zipfile.open(fake_mailbox.name) as zipped_file,
            ZipFile(zipped_file) as inner_zipfile,
        ):
            assert inner_zipfile.namelist() == [
                os.path.basename(fake_email_with_file.file_path)
            ]
            with inner_zipfile.open(
                os.path.basename(fake_email_with_file.file_path)
            ) as inner_zipped_file:
                assert (
                    inner_zipped_file.read().replace(b"\r", b"").strip()
                    == default_storage.open(fake_email_with_file.file_path)
                    .read()
                    .replace(b"\r", b"")
                    .strip()
                )
    assert hasattr(result, "close")
    result.close()
    assert os.listdir(gettempdir()) == []


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_format",
    [
        SupportedEmailDownloadFormats.MBOX,
        SupportedEmailDownloadFormats.MMDF,
        SupportedEmailDownloadFormats.BABYL,
        SupportedEmailDownloadFormats.MBOX.title(),
        SupportedEmailDownloadFormats.MMDF.title(),
        SupportedEmailDownloadFormats.BABYL.title(),
    ],
)
def test_Mailbox_queryset_as_file_mailbox_file(
    fake_file, fake_mailbox, fake_email, fake_email_with_file, file_format
):
    """Tests :func:`core.models.Mailbox.Mailbox.queryset_as_file`
    in case the given format is a mailbox single fileformat.
    """
    assert Mailbox.objects.count() == 1
    assert fake_mailbox.emails.count() == 2

    result = Mailbox.queryset_as_file(Mailbox.objects.all(), file_format)

    assert Mailbox.objects.count() == 1
    assert hasattr(result, "read")
    assert hasattr(result, "name")
    parser_class = file_format_parsers[file_format.lower()]
    with ZipFile(result.name) as zipfile:
        assert fake_mailbox.name in zipfile.namelist()
        with TemporaryDirectory() as tempdir:
            zipfile.extract(fake_mailbox.name, path=tempdir)
            parser = parser_class(os.path.join(tempdir, fake_mailbox.name))
            assert len(list(parser.iterkeys())) == 1
            for key in parser.iterkeys():
                assert (
                    parser.get_bytes(key).replace(b"\r", b"").strip()
                    == default_storage.open(fake_email_with_file.file_path)
                    .read()
                    .replace(b"\r", b"")
                    .strip()
                )
    assert hasattr(result, "close")
    result.close()
    assert os.listdir(gettempdir()) == []


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_format",
    [
        SupportedEmailDownloadFormats.MAILDIR,
        SupportedEmailDownloadFormats.MH,
        SupportedEmailDownloadFormats.MAILDIR.title(),
        SupportedEmailDownloadFormats.MH.title(),
    ],
)
def test_Mailbox_queryset_as_file_mailbox_zip(
    fake_file, fake_mailbox, fake_email, fake_email_with_file, file_format
):
    """Tests :func:`core.models.Mailbox.Mailbox.queryset_as_file`
    in case the given format is a zip of a mailbox directory.
    """
    assert Mailbox.objects.count() == 1
    assert fake_mailbox.emails.count() == 2

    result = Mailbox.queryset_as_file(Mailbox.objects.all(), file_format)

    assert Mailbox.objects.count() == 1
    assert hasattr(result, "read")
    with ZipFile(result) as zipfile:
        assert fake_mailbox.name in zipfile.namelist()
        with TemporaryDirectory() as tempdir:
            with (
                zipfile.open(fake_mailbox.name) as zipped_file,
                ZipFile(zipped_file) as inner_zipfile,
            ):
                inner_zipfile.extractall(tempdir)
            parser_class = file_format_parsers[file_format.lower()]
            parser = parser_class(os.path.join(tempdir, os.listdir(tempdir)[0]))
            assert len(list(parser.iterkeys())) == 1
            for key in parser.iterkeys():
                assert (
                    parser.get_bytes(key).replace(b"\r", b"").strip()
                    == default_storage.open(fake_email_with_file.file_path)
                    .read()
                    .replace(b"\r", b"")
                    .strip()
                )
    assert hasattr(result, "close")
    result.close()
    assert os.listdir(gettempdir()) == []


@pytest.mark.django_db
def test_Mailbox_queryset_as_file__bad_format(fake_mailbox, fake_email):
    """Tests :func:`core.models.Mailbox.Mailbox.queryset_as_file`
    in case the given format is unsupported .
    """
    assert Mailbox.objects.count() == 1

    with pytest.raises(ValueError, match=re.compile("unsupported", re.IGNORECASE)):
        Mailbox.queryset_as_file(Mailbox.objects.all(), "unSupPortEd")

    assert Mailbox.objects.count() == 1


@pytest.mark.django_db
def test_Mailbox_queryset_as_file_empty_queryset():
    """Tests :func:`core.models.Mailbox.Mailbox.queryset_as_file`
    in case the queryset is empty.
    """
    assert Mailbox.objects.count() == 0

    with pytest.raises(Mailbox.DoesNotExist):
        Mailbox.queryset_as_file(
            Mailbox.objects.none(), SupportedEmailDownloadFormats.ZIP_EML
        )

    assert Mailbox.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "DEFAULT_SAVE_ATTACHMENTS, DEFAULT_SAVE_TO_EML",
    [(True, True), (False, False), (True, False), (False, True)],
)
def test_Mailbox_create_from_data__success(
    faker,
    override_config,
    fake_account,
    mock_logger,
    DEFAULT_SAVE_ATTACHMENTS,
    DEFAULT_SAVE_TO_EML,
):
    """Tests :func:`core.models.Account.Account.create_from_data`
    in case of success.
    """
    fake_name = faker.name()

    assert Mailbox.objects.count() == 0
    with override_config(
        DEFAULT_SAVE_ATTACHMENTS=DEFAULT_SAVE_ATTACHMENTS,
        DEFAULT_SAVE_TO_EML=DEFAULT_SAVE_TO_EML,
        THROW_OUT_SPAM=False,
    ):
        new_mailbox = Mailbox.create_from_data(fake_name, "junk", fake_account)

    assert Mailbox.objects.count() == 1
    assert new_mailbox.pk is not None
    assert new_mailbox.name == fake_name
    assert new_mailbox.type == MailboxTypeChoices.JUNK
    assert new_mailbox.save_attachments is DEFAULT_SAVE_ATTACHMENTS
    assert new_mailbox.save_to_eml is DEFAULT_SAVE_TO_EML
    assert new_mailbox.is_healthy
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_Mailbox_create_from_data__duplicate(faker, fake_mailbox, mock_logger):
    """Tests :func:`core.models.Account.Account.create_from_data`
    in case of data that is already in the db.
    """
    fake_type = faker.random_element(MailboxTypeChoices.values)

    assert Mailbox.objects.count() == 1

    new_mailbox = Mailbox.create_from_data(
        fake_mailbox.name, fake_type.title(), fake_mailbox.account
    )

    assert Mailbox.objects.count() == 1
    assert new_mailbox.pk is not None
    assert new_mailbox == fake_mailbox
    assert new_mailbox.type == fake_type
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_healthy
    mock_logger.debug.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "mailbox_name",
    ["Spam", "Junk", "Account/Spam", "Junk-Email", "Emailjunk", "Warning:spam-folder"],
)
def test_Mailbox_create_from_data__ignored__by_name(
    override_config,
    fake_mailbox,
    mock_logger,
    mailbox_name,
):
    """Tests :func:`core.models.Account.Account.create_from_data`
    in case of data that is in the ignorelist.
    """
    assert Mailbox.objects.count() == 1

    with override_config(IGNORED_MAILBOXES_REGEX="(Spam|Junk)"):
        new_mailbox = Mailbox.create_from_data(
            mailbox_name, "Custom", fake_mailbox.account
        )

    assert Mailbox.objects.count() == 1
    assert new_mailbox is None
    mock_logger.debug.assert_called()


def test_Mailbox_create_from_data__ignored__by_type(
    override_config,
    fake_mailbox,
    mock_logger,
):
    """Tests :func:`core.models.Account.Account.create_from_data`
    in case of a type that is in the ignored.
    """
    assert Mailbox.objects.count() == 1

    with override_config(THROW_OUT_SPAM=True):
        new_mailbox = Mailbox.create_from_data("someName", "junk", fake_mailbox.account)

    assert Mailbox.objects.count() == 1
    assert new_mailbox is None
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_Mailbox_create_from_data__unsaved_account(faker):
    """Tests :func:`core.models.Account.Account.create_from_data`
    in case of data that is already in the db.
    """
    fake_name_bytes = faker.name().encode()

    assert Mailbox.objects.count() == 0

    with pytest.raises(ValueError, match=re.compile("account", re.IGNORECASE)):
        Mailbox.create_from_data(fake_name_bytes, "no_type", Account())

    assert Mailbox.objects.count() == 0


@pytest.mark.django_db
def test_Mailbox_has_download__with_email(fake_mailbox, fake_email):
    """Tests :func:`core.models.Mailbox.Mailbox.has_download`."""
    assert fake_mailbox.emails.exists()

    result = fake_mailbox.has_download

    assert result


@pytest.mark.django_db
def test_Mailbox_has_download__no_email(fake_mailbox):
    """Tests :func:`core.models.Mailbox.Mailbox.has_download`."""
    assert not fake_mailbox.emails.exists()

    result = fake_mailbox.has_download

    assert not result


@pytest.mark.django_db
def test_Mailbox_available_download_formats(fake_mailbox):
    """Tests :func:`core.models.Mailbox.Mailbox.available_download_formats`."""
    result = fake_mailbox.available_download_formats

    assert result == SupportedEmailDownloadFormats.choices


@pytest.mark.django_db
def test_Mailbox_get_absolute_url(fake_mailbox):
    """Tests :func:`core.models.Mailbox.Mailbox.get_absolute_url`."""
    result = fake_mailbox.get_absolute_url()

    assert result == reverse(
        f"web:{fake_mailbox.BASENAME}-detail",
        kwargs={"pk": fake_mailbox.pk},
    )


@pytest.mark.django_db
def test_Mailbox_get_absolute_edit_url(fake_mailbox):
    """Tests :func:`core.models.Mailbox.Mailbox.get_absolute_edit_url`."""
    result = fake_mailbox.get_absolute_edit_url()

    assert result == reverse(
        f"web:{fake_mailbox.BASENAME}-edit",
        kwargs={"pk": fake_mailbox.pk},
    )


@pytest.mark.django_db
def test_Mailbox_get_absolute_list_url(fake_mailbox):
    """Tests :func:`core.models.Mailbox.Mailbox.get_absolute_list_url`."""
    result = fake_mailbox.get_absolute_list_url()

    assert result == reverse(
        f"web:{fake_mailbox.BASENAME}-filter-list",
    )


@pytest.mark.django_db
def test_Mailbox_get_absolute_upload_url(fake_mailbox):
    """Tests :func:`core.models.Mailbox.Mailbox.get_absolute_list_url`."""
    result = fake_mailbox.get_absolute_upload_url()

    assert result == reverse(
        f"web:{fake_mailbox.BASENAME}-upload",
        kwargs={"pk": fake_mailbox.pk},
    )
