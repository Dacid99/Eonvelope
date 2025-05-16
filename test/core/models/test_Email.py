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


"""Test module for :mod:`core.models.Email`."""
from __future__ import annotations

import datetime
import os

import pytest
from django.db import IntegrityError
from django.urls import reverse
from model_bakery import baker

import core.models.Email
from core.models.Email import Email
from core.models.Mailbox import Mailbox
from core.models.MailingList import MailingList

from ...conftest import TEST_EMAIL_PARAMETERS
from .test_Attachment import mock_Attachment_save_to_storage


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Mocks :attr:`core.models.Email.logger` of the module."""
    return mocker.patch("core.models.Email.logger", autospec=True)


@pytest.fixture(autouse=True)
def mock_os_remove(mocker):
    """Fixture patching :func`os.remove` to avoid errors."""
    return mocker.patch("core.models.Email.os.remove", autospec=True)


@pytest.fixture
def mock_open(mocker, fake_file_bytes):
    """Fixture to mock the builtin :func:`open`."""
    mock_open = mocker.mock_open(read_data=fake_file_bytes)
    mocker.patch("core.utils.fileManagment.open", mock_open)
    return mock_open


@pytest.fixture
def mock_Storage_getSubdirectory(mocker, faker):
    fake_directory_path = os.path.dirname(faker.file_path())
    mock_Storage_getSubdirectory = mocker.patch(
        "core.models.Storage.Storage.getSubdirectory", autospec=True
    )
    mock_Storage_getSubdirectory.return_value = fake_directory_path
    return mock_Storage_getSubdirectory


@pytest.fixture
def mock_eml2html(mocker, faker):
    mock_eml2html = mocker.patch("core.models.Email.eml2html", autospec=True)
    mock_eml2html.return_value = faker.text()
    return mock_eml2html


@pytest.fixture
def email_with_filepaths(faker, fake_email):
    """Fixture adding filepaths to `email`."""
    fake_email.eml_filepath = faker.file_path(extension="eml")
    fake_email.html_filepath = faker.file_path(extension="png")
    fake_email.save()
    return fake_email


@pytest.fixture
def spy__save(mocker):
    """Fixture spying on :func:`django.db.models.Model.save`."""
    return mocker.spy(core.models.Email.models.Model, "save")


@pytest.fixture
def mock_Email_save_eml_to_storage(mocker):
    """Fixture patching :func:`core.models.Email.Email.save_eml_to_storage`."""
    return mocker.patch("core.models.Email.Email.save_eml_to_storage", autospec=True)


@pytest.fixture
def mock_Email_save_html_to_storage(mocker):
    """Fixture patching :func:`core.models.Email.Email.save_html_to_storage`."""
    return mocker.patch("core.models.Email.Email.save_html_to_storage", autospec=True)


@pytest.fixture
def emailConversation(fake_email):
    """Fixture creating a conversation around `email`."""
    replyMails = baker.make(Email, inReplyTo=fake_email, _quantity=3)
    baker.make(Email, inReplyTo=replyMails[1], _quantity=2)
    replyReplyMail = baker.make(Email, inReplyTo=replyMails[0])
    baker.make(Email, inReplyTo=replyReplyMail)


@pytest.mark.django_db
def test_Email_fields(fake_email):
    """Tests the fields of :class:`core.models.Email.Email`."""

    assert fake_email.message_id is not None
    assert isinstance(fake_email.message_id, str)
    assert fake_email.datetime is not None
    assert isinstance(fake_email.datetime, datetime.datetime)
    assert fake_email.email_subject is not None
    assert isinstance(fake_email.email_subject, str)
    assert fake_email.plain_bodytext is not None
    assert isinstance(fake_email.plain_bodytext, str)
    assert fake_email.html_bodytext is not None
    assert isinstance(fake_email.html_bodytext, str)
    assert fake_email.inReplyTo is None
    assert fake_email.datasize is not None
    assert isinstance(fake_email.datasize, int)
    assert fake_email.eml_filepath is not None
    assert isinstance(fake_email.eml_filepath, str)
    assert fake_email.html_filepath is not None
    assert isinstance(fake_email.html_filepath, str)
    assert fake_email.is_favorite is False

    assert fake_email.mailinglist is not None
    assert isinstance(fake_email.mailinglist, MailingList)
    assert fake_email.mailbox is not None
    assert isinstance(fake_email.mailbox, Mailbox)
    assert fake_email.headers is None
    assert fake_email.x_spam is not None
    assert isinstance(fake_email.x_spam, str)

    assert isinstance(fake_email.updated, datetime.datetime)
    assert fake_email.updated is not None
    assert isinstance(fake_email.created, datetime.datetime)
    assert fake_email.created is not None


@pytest.mark.django_db
def test_Email___str__(fake_email):
    """Tests the string representation of :class:`core.models.Email.Email`."""
    assert fake_email.message_id in str(fake_email)
    assert str(fake_email.datetime) in str(fake_email)
    assert str(fake_email.mailbox) in str(fake_email)


@pytest.mark.django_db
def test_Email_foreign_key_mailbox_deletion(fake_email):
    """Tests the on_delete foreign key constraint on mailbox in :class:`core.models.Email.Email`."""

    fake_email.mailbox.delete()

    with pytest.raises(Email.DoesNotExist):
        fake_email.refresh_from_db()


@pytest.mark.django_db
def test_Email_foreign_key_inReplyTo_deletion(fake_email):
    """Tests the on_delete foreign key constraint on inReplyTo in :class:`core.models.Email.Email`."""

    inReplyToEmail = baker.make(Email, x_spam="NO")
    fake_email.inReplyTo = inReplyToEmail
    fake_email.save()

    fake_email.inReplyTo.delete()

    fake_email.refresh_from_db()
    assert fake_email.inReplyTo is None
    with pytest.raises(Email.DoesNotExist):
        inReplyToEmail.refresh_from_db()


@pytest.mark.django_db
def test_Email_foreign_key_mailingList_deletion(fake_email):
    """Tests the on_delete foreign key constraint on mailinglist in :class:`core.models.Email.Email`."""

    mailingList = baker.make(MailingList)
    fake_email.mailinglist = mailingList
    fake_email.save()

    mailingList.delete()

    with pytest.raises(Email.DoesNotExist):
        fake_email.refresh_from_db()


@pytest.mark.django_db
def test_Email_unique_constraints():
    """Tests the unique constraints of :class:`core.models.Email.Email`."""

    email_1 = baker.make(Email, x_spam="NO", message_id="abc123")
    email_2 = baker.make(Email, x_spam="NO", message_id="abc123")
    assert email_1.message_id == email_2.message_id
    assert email_1.mailbox != email_2.mailbox

    mailbox = baker.make(Mailbox)

    email_1 = baker.make(Email, x_spam="NO", mailbox=mailbox)
    email_2 = baker.make(Email, x_spam="NO", mailbox=mailbox)
    assert email_1.message_id != email_2.message_id
    assert email_1.mailbox == email_2.mailbox

    baker.make(Email, x_spam="NO", message_id="abc123", mailbox=mailbox)
    with pytest.raises(IntegrityError):
        baker.make(Email, x_spam="NO", message_id="abc123", mailbox=mailbox)


@pytest.mark.django_db
def test_Email_delete_emailfiles_success(
    mock_logger, email_with_filepaths, mock_os_remove
):
    """Tests :func:`core.models.Email.Email.delete`
    if the file removal is successful.
    """
    email_with_filepaths.delete()

    mock_os_remove.assert_any_call(email_with_filepaths.eml_filepath)
    mock_os_remove.assert_any_call(email_with_filepaths.html_filepath)
    with pytest.raises(Email.DoesNotExist):
        email_with_filepaths.refresh_from_db()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "side_effects",
    [
        [Exception, None],
        [None, Exception],
        [Exception, Exception],
    ],
)
def test_Email_delete_emailfiles_remove_error(
    mock_logger, email_with_filepaths, mock_os_remove, side_effects
):
    """Tests :func:`core.models.Email.Email.delete`
    if the file removal raises an exception.
    """
    mock_os_remove.side_effect = side_effects

    email_with_filepaths.delete()

    mock_os_remove.assert_any_call(email_with_filepaths.eml_filepath)
    mock_os_remove.assert_any_call(email_with_filepaths.html_filepath)
    with pytest.raises(Email.DoesNotExist):
        email_with_filepaths.refresh_from_db()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.exception.assert_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
def test_Email_delete_email_delete_error(
    mocker, mock_logger, email_with_filepaths, mock_os_remove
):
    """Tests :func:`core.models.Email.Email.delete`
    if delete raises an exception.
    """
    mock_delete = mocker.patch(
        "core.models.Email.models.Model.delete",
        autospec=True,
        side_effect=AssertionError,
    )

    with pytest.raises(AssertionError):
        email_with_filepaths.delete()

    mock_delete.assert_called_once()
    mock_os_remove.assert_not_called()
    mock_logger.debug.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "save_to_eml, save_to_html, expected_save_eml_to_storage_call, expected_save_html_to_storage_call",
    [
        (True, True, True, True),
        (False, False, False, False),
        (True, False, True, False),
        (False, True, False, True),
    ],
)
def test_Email_save_with_data_success(
    fake_email,
    mock_message,
    spy__save,
    mock_Email_save_eml_to_storage,
    mock_Email_save_html_to_storage,
    save_to_eml,
    save_to_html,
    expected_save_eml_to_storage_call,
    expected_save_html_to_storage_call,
):
    """Tests :func:`core.models.Email.Email.save`
    in case of success with data to be saved.
    """
    fake_email.mailbox.save_toEML = save_to_eml
    fake_email.mailbox.save_toHTML = save_to_html

    fake_email.save(emailData=mock_message)

    spy__save.assert_called_once_with(fake_email)
    if expected_save_eml_to_storage_call:
        mock_Email_save_eml_to_storage.assert_called_with(fake_email, mock_message)
    else:
        mock_Email_save_eml_to_storage.assert_not_called()
    if expected_save_html_to_storage_call:
        mock_Email_save_html_to_storage.assert_called_with(fake_email, mock_message)
    else:
        mock_Email_save_html_to_storage.assert_not_called()


@pytest.mark.django_db
def test_Email_save_no_data(
    fake_email,
    spy__save,
    mock_Email_save_eml_to_storage,
    mock_Email_save_html_to_storage,
):
    """Tests :func:`core.models.Email.Email.save`
    in case of success without data to be saved.
    """
    fake_email.mailbox.save_toEML = True

    fake_email.save()

    spy__save.assert_called_once_with(fake_email)
    mock_Email_save_eml_to_storage.assert_not_called()
    mock_Email_save_html_to_storage.assert_not_called()


@pytest.mark.django_db
def test_Email_save_with_data_failure(
    fake_email,
    mock_message,
    spy__save,
    mock_Email_save_eml_to_storage,
    mock_Email_save_html_to_storage,
):
    """Tests :func:`core.models.Email.Email.save`
    in case of success saving data fails with an exception.
    """
    mock_Email_save_eml_to_storage.side_effect = AssertionError
    fake_email.mailbox.save_toEML = True

    with pytest.raises(AssertionError):
        fake_email.save(emailData=mock_message)

    spy__save.assert_called()
    mock_Email_save_eml_to_storage.assert_called()
    mock_Email_save_html_to_storage.assert_not_called()


@pytest.mark.django_db
def test_save_eml_to_storage_success(
    fake_file_bytes,
    fake_email,
    mock_logger,
    mock_open,
    mock_Storage_getSubdirectory,
):
    fake_email.eml_filepath = None

    fake_email.save_eml_to_storage(fake_file_bytes)

    mock_Storage_getSubdirectory.assert_called_once_with(fake_email.message_id)
    mock_open.assert_called_once_with(
        os.path.join(
            mock_Storage_getSubdirectory.return_value,
            fake_email.message_id + ".eml",
        ),
        "wb",
    )
    mock_open.return_value.write.assert_called_once_with(fake_file_bytes)
    fake_email.refresh_from_db()
    assert fake_email.eml_filepath == os.path.join(
        mock_Storage_getSubdirectory.return_value, fake_email.message_id + ".eml"
    )
    mock_logger.debug.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_save_eml_to_storage_file_path_set(
    fake_file_bytes,
    email_with_filepaths,
    mock_logger,
    mock_open,
    mock_Storage_getSubdirectory,
):
    previous_file_path = email_with_filepaths.eml_filepath

    email_with_filepaths.save_eml_to_storage(fake_file_bytes)

    mock_Storage_getSubdirectory.assert_not_called()
    mock_open.assert_not_called()
    email_with_filepaths.refresh_from_db()
    assert email_with_filepaths.eml_filepath == previous_file_path
    mock_logger.debug.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_save_eml_to_storage_open_osError(
    fake_file_bytes,
    fake_email,
    mock_logger,
    mock_open,
    mock_Storage_getSubdirectory,
):
    fake_email.eml_filepath = None
    mock_open.side_effect = OSError

    fake_email.save_eml_to_storage(fake_file_bytes)

    mock_Storage_getSubdirectory.assert_called_once_with(fake_email.message_id)
    mock_open.assert_called_once_with(
        os.path.join(
            mock_Storage_getSubdirectory.return_value,
            fake_email.message_id + ".eml",
        ),
        "wb",
    )
    mock_open.return_value.write.assert_not_called()
    assert fake_email.eml_filepath is None
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_save_eml_to_storage_write_osError(
    fake_file_bytes,
    fake_email,
    mock_logger,
    mock_open,
    mock_Storage_getSubdirectory,
):
    fake_email.eml_filepath = None
    mock_open.return_value.write.side_effect = OSError

    fake_email.save_eml_to_storage(fake_file_bytes)

    mock_Storage_getSubdirectory.assert_called_once_with(fake_email.message_id)
    mock_open.assert_called_once_with(
        os.path.join(
            mock_Storage_getSubdirectory.return_value,
            fake_email.message_id + ".eml",
        ),
        "wb",
    )
    mock_open.return_value.write.assert_called_once_with(fake_file_bytes)
    assert fake_email.eml_filepath is None
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_save_html_to_storage_success(
    fake_file_bytes,
    fake_email,
    mock_logger,
    mock_open,
    mock_eml2html,
    mock_Storage_getSubdirectory,
):
    fake_email.html_filepath = None

    fake_email.save_html_to_storage(fake_file_bytes)

    mock_Storage_getSubdirectory.assert_called_once_with(fake_email.message_id)
    mock_open.assert_called_once_with(
        os.path.join(
            mock_Storage_getSubdirectory.return_value,
            fake_email.message_id + ".html",
        ),
        "wb",
    )
    mock_eml2html.assert_called_once_with(fake_file_bytes)
    mock_open.return_value.write.assert_called_once_with(
        mock_eml2html.return_value.encode()
    )
    fake_email.refresh_from_db()
    assert fake_email.html_filepath == os.path.join(
        mock_Storage_getSubdirectory.return_value, fake_email.message_id + ".html"
    )
    mock_logger.debug.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_save_html_to_storage_file_path_set(
    fake_file_bytes,
    email_with_filepaths,
    mock_logger,
    mock_open,
    mock_eml2html,
    mock_Storage_getSubdirectory,
):
    previous_file_path = email_with_filepaths.html_filepath

    email_with_filepaths.save_html_to_storage(fake_file_bytes)

    mock_Storage_getSubdirectory.assert_not_called()
    mock_eml2html.assert_not_called()
    mock_open.assert_not_called()
    email_with_filepaths.refresh_from_db()
    assert email_with_filepaths.html_filepath == previous_file_path
    mock_logger.debug.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_save_html_to_storage_open_osError(
    fake_file_bytes,
    fake_email,
    mock_logger,
    mock_open,
    mock_eml2html,
    mock_Storage_getSubdirectory,
):
    fake_email.html_filepath = None
    mock_open.side_effect = OSError

    fake_email.save_html_to_storage(fake_file_bytes)

    mock_Storage_getSubdirectory.assert_called_once_with(fake_email.message_id)
    mock_open.assert_called_once_with(
        os.path.join(
            mock_Storage_getSubdirectory.return_value,
            fake_email.message_id + ".html",
        ),
        "wb",
    )
    mock_eml2html.assert_not_called()
    mock_open.return_value.write.assert_not_called()
    assert fake_email.html_filepath is None
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_save_html_to_storage_write_osError(
    fake_file_bytes,
    fake_email,
    mock_logger,
    mock_open,
    mock_eml2html,
    mock_Storage_getSubdirectory,
):
    fake_email.html_filepath = None
    mock_open.return_value.write.side_effect = OSError

    fake_email.save_html_to_storage(fake_file_bytes)

    mock_Storage_getSubdirectory.assert_called_once_with(fake_email.message_id)
    mock_open.assert_called_once_with(
        os.path.join(
            mock_Storage_getSubdirectory.return_value,
            fake_email.message_id + ".html",
        ),
        "wb",
    )
    mock_eml2html.assert_called_once_with(fake_file_bytes)
    mock_open.return_value.write.assert_called_once_with(
        mock_eml2html.return_value.encode()
    )
    assert fake_email.html_filepath is None
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "start_id, expected_len",
    [(1, 8), (2, 3), (3, 3), (4, 1), (5, 1), (6, 1), (7, 2), (8, 1)],
)
def test_Email_subConversation(emailConversation, start_id, expected_len):
    """Tests :func:`core.models.Email.Email.subConversation`."""
    startEmail = Email.objects.get(id=start_id)

    subConversationEmails = startEmail.subConversation()

    assert len(subConversationEmails) == expected_len


@pytest.mark.django_db
@pytest.mark.parametrize("start_id", [1, 2, 3, 4, 5, 6, 7, 8])
def test_Email_fullConversation(emailConversation, start_id):
    """Tests :func:`core.models.Email.Email.fullConversation`."""
    startEmail = Email.objects.get(id=start_id)

    subConversationEmails = startEmail.fullConversation()

    assert len(subConversationEmails) == 8


@pytest.mark.django_db
@pytest.mark.parametrize(
    "x_spam, expectedResult",
    [
        (None, False),
        ("", False),
        ("YES", True),
        ("NO", False),
        ("NO, YES", True),
        ("YES, YES", True),
        ("NO, NO", False),
        ("CRAZY", False),
    ],
)
def test_Email_isSpam(fake_email, x_spam, expectedResult):
    """Tests :func:`core.models.Email.Email.isSpam`."""
    fake_email.x_spam = x_spam

    result = fake_email.isSpam()

    assert result is expectedResult


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_email_path, expected_email_features, expected_correspondents_features,expected_attachments_features",
    TEST_EMAIL_PARAMETERS,
)
def test_Email_createFromEmailBytes_success(
    override_config,
    fake_mailbox,
    mock_logger,
    mock_Email_save_eml_to_storage,
    mock_Email_save_html_to_storage,
    mock_Attachment_save_to_storage,
    test_email_path,
    expected_email_features,
    expected_correspondents_features,
    expected_attachments_features,
):
    """Tests :func:`core.models.Email.Email.createFromEmailBytes`
    in case of success.
    """
    with open(test_email_path, "br") as test_email_file:
        test_email_bytes = test_email_file.read()

    with override_config(THROW_OUT_SPAM=False):
        result = Email.createFromEmailBytes(test_email_bytes, mailbox=fake_mailbox)

    assert isinstance(result, Email)
    assert result.pk is not None
    assert result.message_id == expected_email_features["message_id"]
    assert result.email_subject == expected_email_features["email_subject"]
    assert result.x_spam == expected_email_features["x_spam"]
    assert result.plain_bodytext == expected_email_features["plain_bodytext"]
    assert result.html_bodytext == expected_email_features["html_bodytext"]
    assert result.attachments.count() == len(expected_attachments_features)
    for item in result.attachments.all():
        assert item.file_name in expected_attachments_features
        assert (
            item.content_disposition
            == expected_attachments_features[item.file_name]["content_disposition"]
        )
        assert (
            item.content_maintype
            == expected_attachments_features[item.file_name]["content_maintype"]
        )
        assert (
            item.content_subtype
            == expected_attachments_features[item.file_name]["content_subtype"]
        )
        assert (
            item.content_id
            == expected_attachments_features[item.file_name]["content_id"]
        )
    assert result.emailcorrespondents.count() == sum(
        [
            len(correspondents)
            for correspondents in expected_correspondents_features.values()
        ]
    )
    for item in result.emailcorrespondents.all():
        assert item.mention in expected_correspondents_features
        assert (
            item.correspondent.email_address
            in expected_correspondents_features[item.mention]
        )
    assert len(result.headers) == expected_email_features["header_count"]
    assert result.mailbox == fake_mailbox
    if expected_attachments_features:
        mock_Attachment_save_to_storage.assert_called()
    mock_Email_save_eml_to_storage.assert_called()
    mock_Email_save_html_to_storage.assert_called()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
def test_Email_createFromEmailBytes_duplicate(
    override_config,
    fake_email,
    mock_logger,
    mock_Email_save_eml_to_storage,
    mock_Email_save_html_to_storage,
    mock_Attachment_save_to_storage,
):
    """Tests :func:`core.models.Email.Email.createFromEmailBytes`
    in case the email to be parsed is already in the database.
    """
    with override_config(THROW_OUT_SPAM=False):
        result = Email.createFromEmailBytes(
            f"Message-ID: {fake_email.message_id}".encode(), fake_email.mailbox
        )

    assert result is None
    mock_Attachment_save_to_storage.assert_not_called()
    mock_Email_save_eml_to_storage.assert_not_called()
    mock_Email_save_html_to_storage.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.exception.assert_not_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "X_Spam_Flag, THROW_OUT_SPAM, expected_isNone",
    [
        ("YES", True, True),
        ("NO", True, False),
        ("YES, NO", True, True),
        ("NO, YES", True, True),
        ("NO, NO", True, False),
        ("SOMETHING", True, False),
        ("YES", False, False),
        ("NO", False, False),
        ("YES, NO", False, False),
        ("NO, YES", False, False),
        ("NO, NO", False, False),
        ("SOMETHING", False, False),
    ],
)
def test_Email_createFromEmailBytes_spam(
    override_config,
    fake_mailbox,
    mock_logger,
    mock_Email_save_eml_to_storage,
    mock_Email_save_html_to_storage,
    mock_Attachment_save_to_storage,
    X_Spam_Flag,
    THROW_OUT_SPAM,
    expected_isNone,
):
    """Tests :func:`core.models.Email.Email.createFromEmailBytes`
    with regard to spam emails.
    """
    with override_config(THROW_OUT_SPAM=THROW_OUT_SPAM):
        result = Email.createFromEmailBytes(
            f"X-Spam-Flag: {X_Spam_Flag}".encode(), fake_mailbox
        )

    assert (result is None) is expected_isNone
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.exception.assert_not_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
def test_Email_createFromEmailBytes_dberror(
    mocker, override_config, fake_mailbox, mock_logger
):
    """Tests :func:`core.models.Email.Email.createFromEmailBytes`
    in case an database :class:`django.db.IntegrityError` occurs.
    """
    mock_Email_save = mocker.patch(
        "core.models.Email.Email.save",
        autospec=True,
        side_effect=IntegrityError,
    )

    with override_config(THROW_OUT_SPAM=False):
        result = Email.createFromEmailBytes(b"Message-ID: something", fake_mailbox)

    assert result is None
    mock_Email_save.assert_called()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.exception.assert_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "eml_filepath, expected_has_download",
    [
        (None, False),
        ("some/file/path", True),
    ],
)
def test_Email_has_download(fake_email, eml_filepath, expected_has_download):
    """Tests :func:`core.models.Email.Email.has_download` in the two relevant cases."""
    fake_email.eml_filepath = eml_filepath

    result = fake_email.has_download

    assert result == expected_has_download


@pytest.mark.django_db
@pytest.mark.parametrize(
    "html_filepath, expected_has_thumbnail",
    [
        (None, False),
        ("some/file/path", True),
    ],
)
def test_Email_has_thumbnail(fake_email, html_filepath, expected_has_thumbnail):
    """Tests :func:`core.models.Email.Email.has_download` in the two relevant cases."""
    fake_email.html_filepath = html_filepath

    result = fake_email.has_thumbnail

    assert result is expected_has_thumbnail


@pytest.mark.django_db
def test_Email_get_absolute_thumbnail_url(fake_email):
    """Tests :func:`core.models.Email.Email.get_absolute_thumbnail_url`."""
    result = fake_email.get_absolute_thumbnail_url()

    assert result == reverse(
        f"api:v1:{fake_email.BASENAME}-download-html",
        kwargs={"pk": fake_email.pk},
    )


@pytest.mark.django_db
def test_Email_get_absolute_url(fake_email):
    """Tests :func:`core.models.Email.Email.get_absolute_url`."""
    result = fake_email.get_absolute_url()

    assert result == reverse(
        f"web:{fake_email.BASENAME}-detail", kwargs={"pk": fake_email.pk}
    )


@pytest.mark.django_db
def test_Email_get_absolute_list_url(fake_email):
    """Tests :func:`core.models.Email.Email.get_absolute_list_url`."""
    result = fake_email.get_absolute_list_url()

    assert result == reverse(
        f"web:{fake_email.BASENAME}-filter-list",
    )
