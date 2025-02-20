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


"""Test module for :mod:`core.models.EMailModel`.

Fixtures:
    :func:`fixture_emailModel`: Creates an :class:`core.models.EMailModel.EMailModel` instance for testing.
"""

import datetime
from email.message import Message

import pytest
from django.db import IntegrityError
from faker import Faker
from model_bakery import baker

from core.models.EMailModel import EMailModel
from core.models.MailboxModel import MailboxModel
from core.models.MailingListModel import MailingListModel

from .test_MailboxModel import fixture_mailboxModel


@pytest.fixture(name="mock_logger", autouse=True)
def fixture_mock_logger(mocker):
    """Mocks :attr:`core.models.EMailModel.logger` of the module."""
    return mocker.patch("core.models.EMailModel.logger")


@pytest.fixture(name="email")
def fixture_emailModel() -> EMailModel:
    """Creates an :class:`core.models.EMailModel.EMailModel`.

    Returns:
        The email instance for testing.
    """
    return baker.make(EMailModel, x_spam="NO")


@pytest.fixture(name="emailConversation")
def fixture_emailConversation(email):
    replyMails = baker.make(EMailModel, x_spam="NO", inReplyTo=email, _quantity=3)
    baker.make(EMailModel, x_spam="NO", inReplyTo=replyMails[1], _quantity=2)
    replyReplyMail = baker.make(EMailModel, x_spam="NO", inReplyTo=replyMails[0])
    baker.make(EMailModel, x_spam="NO", inReplyTo=replyReplyMail)


@pytest.mark.django_db
def test_EMailModel_creation(email):
    """Tests the correct default creation of :class:`core.models.EMailModel.EMailModel`."""

    assert email.message_id is not None
    assert isinstance(email.message_id, str)
    assert email.datetime is not None
    assert isinstance(email.datetime, datetime.datetime)
    assert email.email_subject is None
    assert email.plain_bodytext is not None
    assert isinstance(email.plain_bodytext, str)
    assert email.html_bodytext is not None
    assert isinstance(email.html_bodytext, str)
    assert email.inReplyTo is None
    assert email.datasize is not None
    assert isinstance(email.datasize, int)
    assert email.eml_filepath is None
    assert email.prerender_filepath is None
    assert email.is_favorite is False

    assert email.mailinglist is None
    assert email.mailbox is not None
    assert isinstance(email.mailbox, MailboxModel)
    assert email.headers is None
    assert email.x_spam == "NO"

    assert isinstance(email.updated, datetime.datetime)
    assert email.updated is not None
    assert isinstance(email.created, datetime.datetime)
    assert email.created is not None

    assert email.message_id in str(email)
    assert str(email.datetime) in str(email)
    assert str(email.mailbox) in str(email)


@pytest.mark.django_db
def test_EMailModel_foreign_key_mailbox_deletion(email):
    """Tests the on_delete foreign key constraint on mailbox in :class:`core.models.EMailModel.EMailModel`."""

    email.mailbox.delete()

    with pytest.raises(EMailModel.DoesNotExist):
        email.refresh_from_db()


@pytest.mark.django_db
def test_EMailModel_foreign_key_inReplyTo_deletion(email):
    """Tests the on_delete foreign key constraint on inReplyTo in :class:`core.models.EMailModel.EMailModel`."""

    inReplyToEmail = baker.make(EMailModel, x_spam="NO")
    email.inReplyTo = inReplyToEmail
    email.save()

    email.inReplyTo.delete()

    email.refresh_from_db()
    assert email.inReplyTo is None
    with pytest.raises(EMailModel.DoesNotExist):
        inReplyToEmail.refresh_from_db()


@pytest.mark.django_db
def test_EMailModel_foreign_key_mailingList_deletion(email):
    """Tests the on_delete foreign key constraint on mailinglist in :class:`core.models.EMailModel.EMailModel`."""

    mailingList = baker.make(MailingListModel)
    email.mailinglist = mailingList
    email.save()

    mailingList.delete()

    with pytest.raises(EMailModel.DoesNotExist):
        email.refresh_from_db()


@pytest.mark.django_db
def test_EMailModel_unique():
    """Tests the unique constraints of :class:`core.models.EMailModel.EMailModel`."""

    email_1 = baker.make(EMailModel, x_spam="NO", message_id="abc123")
    email_2 = baker.make(EMailModel, x_spam="NO", message_id="abc123")
    assert email_1.message_id == email_2.message_id
    assert email_1.mailbox != email_2.mailbox

    mailbox = baker.make(MailboxModel)

    email_1 = baker.make(EMailModel, x_spam="NO", mailbox=mailbox)
    email_2 = baker.make(EMailModel, x_spam="NO", mailbox=mailbox)
    assert email_1.message_id != email_2.message_id
    assert email_1.mailbox == email_2.mailbox

    baker.make(EMailModel, x_spam="NO", message_id="abc123", mailbox=mailbox)
    with pytest.raises(IntegrityError):
        baker.make(EMailModel, x_spam="NO", message_id="abc123", mailbox=mailbox)


@pytest.mark.django_db
def test_delete_email_success(mocker, mock_logger, email):
    """Tests :func:`core.models.EMailModel.EMailModel.delete`
    if the file removal is successful.
    """
    mock_os_remove = mocker.patch("core.models.EMailModel.os.remove")
    email.eml_filepath = Faker().file_path(extension="eml")
    email.prerender_filepath = Faker().file_path(extension="png")
    email.save()
    eml_file_path = email.eml_filepath
    prerender_file_path = email.prerender_filepath

    email.delete()

    with pytest.raises(EMailModel.DoesNotExist):
        email.refresh_from_db()
    mock_os_remove.assert_any_call(eml_file_path)
    mock_os_remove.assert_any_call(prerender_file_path)
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
def test_delete_email_remove_error(mocker, email, mock_logger, side_effects):
    """Tests :func:`core.models.EMailModel.EMailModel.delete`
    if the file removal throws an exception.
    """
    mock_os_remove = mocker.patch(
        "core.models.EMailModel.os.remove", side_effect=side_effects
    )
    email.eml_filepath = Faker().file_path(extension="eml")
    email.prerender_filepath = Faker().file_path(extension="png")
    email.save()
    eml_file_path = email.eml_filepath
    prerender_file_path = email.prerender_filepath

    email.delete()

    with pytest.raises(EMailModel.DoesNotExist):
        email.refresh_from_db()
    mock_os_remove.assert_any_call(eml_file_path)
    mock_os_remove.assert_any_call(prerender_file_path)
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
def test_delete_email_delete_error(mocker, email, mock_logger):
    """Tests :func:`core.models.EMailModel.EMailModel.delete`
    if delete throws an exception.
    """
    mock_delete = mocker.patch(
        "core.models.EMailModel.models.Model.delete", side_effect=ValueError
    )
    mock_os_remove = mocker.patch("core.models.EMailModel.os.remove")
    email.eml_filepath = Faker().file_path(extension="eml")
    email.prerender_filepath = Faker().file_path(extension="png")
    email.save()

    with pytest.raises(ValueError):
        email.delete()

    mock_delete.assert_called_once()
    mock_os_remove.assert_not_called()
    mock_logger.debug.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("save_to_eml, expectedCalls", [(True, 1), (False, 0)])
def test_save_data_settings(mocker, email, save_to_eml, expectedCalls):
    mock_super_save = mocker.patch("core.models.EMailModel.models.Model.save")
    mock_save_to_storage = mocker.patch(
        "core.models.EMailModel.EMailModel.save_to_storage"
    )
    email.mailbox.save_toEML = save_to_eml
    mock_data = mocker.MagicMock(spec=Message)

    email.save(attachmentData=mock_data)

    mock_save_to_storage.call_count == expectedCalls
    mock_super_save.assert_called()


@pytest.mark.django_db
def test_save_no_data(mocker, email):
    mock_super_save = mocker.patch("core.models.EMailModel.models.Model.save")
    mock_save_to_storage = mocker.patch(
        "core.models.EMailModel.EMailModel.save_to_storage"
    )
    email.mailbox.save_toEML = True

    email.save()

    mock_super_save.assert_called_once_with()
    mock_save_to_storage.assert_not_called()


@pytest.mark.django_db
def test_save_data_failure(mocker, email):
    mock_super_save = mocker.patch("core.models.EMailModel.models.Model.save")
    mock_save_to_storage = mocker.patch(
        "core.models.EMailModel.EMailModel.save_to_storage",
        side_effect=Exception,
    )
    email.mailbox.save_toEML = True
    mock_data = mocker.MagicMock(spec=Message)

    with pytest.raises(Exception):
        email.save(emailData=mock_data)

    mock_super_save.assert_called()
    mock_save_to_storage.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "start_id, expected_len",
    [(1, 8), (2, 3), (3, 3), (4, 1), (5, 1), (6, 1), (7, 2), (8, 1)],
)
def test_EMailModel_subConversation(emailConversation, start_id, expected_len):
    """Tests the on_delete foreign key constraint on account in :class:`core.models.EMailModel.EMailModel`."""
    startEmail = EMailModel.objects.get(id=start_id)

    subConversationEmails = startEmail.subConversation()

    assert len(subConversationEmails) == expected_len


@pytest.mark.django_db
@pytest.mark.parametrize("start_id", [1, 2, 3, 4, 5, 6, 7, 8])
def test_EMailModel_fullConversation(emailConversation, start_id):
    """Tests the on_delete foreign key constraint on account in :class:`core.models.EMailModel.EMailModel`."""
    startEmail = EMailModel.objects.get(id=start_id)

    subConversationEmails = startEmail.fullConversation()

    assert len(subConversationEmails) == 8


@pytest.mark.django_db
@pytest.mark.parametrize(
    "x_spam, expectedResult", [(None, False), ("YES", True), ("NO", False)]
)
def test_EMailModel_isSpam(email, x_spam, expectedResult):
    email.x_spam = x_spam

    result = email.isSpam()

    assert result is expectedResult


@pytest.mark.django_db(transaction=True)
def test_EMailModel_createFromEmailBytes(mocker, attachmentEmailData, mailbox):
    mock_EMailModel_save_to_storage = mocker.patch(
        "core.models.EMailModel.EMailModel.save_to_storage"
    )
    mock_EMailModel_render_to_storage = mocker.patch(
        "core.models.EMailModel.EMailModel.render_to_storage"
    )
    mock_AttachmentModel_save_to_storage = mocker.patch(
        "core.models.EMailModel.AttachmentModel.save_to_storage"
    )

    email = EMailModel.createFromEmailBytes(attachmentEmailData, mailbox=mailbox)

    assert email.message_id == "<e047e14d-2397-435b-baf6-8e8b7423f860@out.de>"
    assert email.email_subject == "Whats up"
    assert email.x_spam == "NO"
    assert email.plain_bodytext == "this a test to see how ur doin\n\n\n\n\n"
    assert email.html_bodytext == ""
    assert email.attachments.count() == 1
    assert email.correspondents.count() == 5
    mock_AttachmentModel_save_to_storage.assert_called()
    mock_EMailModel_save_to_storage.assert_called()
    mock_EMailModel_render_to_storage.assert_called()
