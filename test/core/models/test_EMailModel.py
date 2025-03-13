# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable emailModel archiving server
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
    :func:`fixture_emailModelModel`: Creates an :class:`core.models.EMailModel.EMailModel` instance for testing.
"""
from __future__ import annotations

import datetime

import pytest
from django.db import IntegrityError
from model_bakery import baker

import core.models.EMailModel
from core.models.EMailModel import EMailModel
from core.models.MailboxModel import MailboxModel
from core.models.MailingListModel import MailingListModel

from ..conftest import TEST_EMAIL_PARAMETERS
from .test_AttachmentModel import mock_AttachmentModel_save_to_storage


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Mocks :attr:`core.models.EMailModel.logger` of the module."""
    return mocker.patch("core.models.EMailModel.logger", autospec=True)


@pytest.fixture(autouse=True)
def mock_os_remove(mocker):
    return mocker.patch("core.models.EMailModel.os.remove", autospec=True)


@pytest.fixture
def emailModel_with_filepaths(faker, emailModel):
    emailModel.eml_filepath = faker.file_path(extension="eml")
    emailModel.prerender_filepath = faker.file_path(extension="png")
    emailModel.save()
    return emailModel


@pytest.fixture
def spy_Model_save(mocker):
    return mocker.spy(core.models.EMailModel.models.Model, "save")


@pytest.fixture
def mock_EMailModel_save_to_storage(mocker):
    return mocker.patch(
        "core.models.EMailModel.EMailModel.save_to_storage", autospec=True
    )


@pytest.fixture
def mock_EMailModel_render_to_storage(mocker):
    return mocker.patch(
        "core.models.EMailModel.EMailModel.render_to_storage", autospec=True
    )


@pytest.fixture
def emailConversation(emailModel) -> None:
    replyMails = baker.make(EMailModel, inReplyTo=emailModel, _quantity=3)
    baker.make(EMailModel, inReplyTo=replyMails[1], _quantity=2)
    replyReplyMail = baker.make(EMailModel, inReplyTo=replyMails[0])
    baker.make(EMailModel, inReplyTo=replyReplyMail)


@pytest.mark.django_db
def test_EMailModel_default_creation(emailModel):
    """Tests the correct default creation of :class:`core.models.EMailModel.EMailModel`."""

    assert emailModel.message_id is not None
    assert isinstance(emailModel.message_id, str)
    assert emailModel.datetime is not None
    assert isinstance(emailModel.datetime, datetime.datetime)
    assert emailModel.email_subject is not None
    assert isinstance(emailModel.email_subject, str)
    assert emailModel.plain_bodytext is not None
    assert isinstance(emailModel.plain_bodytext, str)
    assert emailModel.html_bodytext is not None
    assert isinstance(emailModel.html_bodytext, str)
    assert emailModel.inReplyTo is None
    assert emailModel.datasize is not None
    assert isinstance(emailModel.datasize, int)
    assert emailModel.eml_filepath is None
    assert emailModel.prerender_filepath is None
    assert emailModel.is_favorite is False

    assert emailModel.mailinglist is None
    assert emailModel.mailbox is not None
    assert isinstance(emailModel.mailbox, MailboxModel)
    assert emailModel.headers is None
    assert emailModel.x_spam is not None
    assert isinstance(emailModel.x_spam, str)

    assert isinstance(emailModel.updated, datetime.datetime)
    assert emailModel.updated is not None
    assert isinstance(emailModel.created, datetime.datetime)
    assert emailModel.created is not None


@pytest.mark.django_db
def test_EMailModel___str__(emailModel):
    assert emailModel.message_id in str(emailModel)
    assert str(emailModel.datetime) in str(emailModel)
    assert str(emailModel.mailbox) in str(emailModel)


@pytest.mark.django_db
def test_EMailModel_foreign_key_mailbox_deletion(emailModel):
    """Tests the on_delete foreign key constraint on mailbox in :class:`core.models.EMailModel.EMailModel`."""

    emailModel.mailbox.delete()

    with pytest.raises(EMailModel.DoesNotExist):
        emailModel.refresh_from_db()


@pytest.mark.django_db
def test_EMailModel_foreign_key_inReplyTo_deletion(emailModel):
    """Tests the on_delete foreign key constraint on inReplyTo in :class:`core.models.EMailModel.EMailModel`."""

    inReplyToEmail = baker.make(EMailModel, x_spam="NO")
    emailModel.inReplyTo = inReplyToEmail
    emailModel.save()

    emailModel.inReplyTo.delete()

    emailModel.refresh_from_db()
    assert emailModel.inReplyTo is None
    with pytest.raises(EMailModel.DoesNotExist):
        inReplyToEmail.refresh_from_db()


@pytest.mark.django_db
def test_EMailModel_foreign_key_mailingList_deletion(emailModel):
    """Tests the on_delete foreign key constraint on mailinglist in :class:`core.models.EMailModel.EMailModel`."""

    mailingListModel = baker.make(MailingListModel)
    emailModel.mailinglist = mailingListModel
    emailModel.save()

    mailingListModel.delete()

    with pytest.raises(EMailModel.DoesNotExist):
        emailModel.refresh_from_db()


@pytest.mark.django_db
def test_EMailModel_unique():
    """Tests the unique constraints of :class:`core.models.EMailModel.EMailModel`."""

    emailModel_1 = baker.make(EMailModel, x_spam="NO", message_id="abc123")
    emailModel_2 = baker.make(EMailModel, x_spam="NO", message_id="abc123")
    assert emailModel_1.message_id == emailModel_2.message_id
    assert emailModel_1.mailbox != emailModel_2.mailbox

    mailbox = baker.make(MailboxModel)

    emailModel_1 = baker.make(EMailModel, x_spam="NO", mailbox=mailbox)
    emailModel_2 = baker.make(EMailModel, x_spam="NO", mailbox=mailbox)
    assert emailModel_1.message_id != emailModel_2.message_id
    assert emailModel_1.mailbox == emailModel_2.mailbox

    baker.make(EMailModel, x_spam="NO", message_id="abc123", mailbox=mailbox)
    with pytest.raises(IntegrityError):
        baker.make(EMailModel, x_spam="NO", message_id="abc123", mailbox=mailbox)


@pytest.mark.django_db
def test_delete_emailModel_success(
    mock_logger, emailModel_with_filepaths, mock_os_remove
):
    """Tests :func:`core.models.EMailModel.EMailModel.delete`
    if the file removal is successful.
    """
    emailModel_with_filepaths.delete()

    mock_os_remove.assert_any_call(emailModel_with_filepaths.eml_filepath)
    mock_os_remove.assert_any_call(emailModel_with_filepaths.prerender_filepath)
    with pytest.raises(EMailModel.DoesNotExist):
        emailModel_with_filepaths.refresh_from_db()
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
def test_delete_emailModel_remove_error(
    mock_logger, emailModel_with_filepaths, mock_os_remove, side_effects
) -> None:
    """Tests :func:`core.models.EMailModel.EMailModel.delete`
    if the file removal throws an exception.
    """
    mock_os_remove.side_effect = side_effects

    emailModel_with_filepaths.delete()

    mock_os_remove.assert_any_call(emailModel_with_filepaths.eml_filepath)
    mock_os_remove.assert_any_call(emailModel_with_filepaths.prerender_filepath)
    with pytest.raises(EMailModel.DoesNotExist):
        emailModel_with_filepaths.refresh_from_db()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.exception.assert_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
def test_delete_emailModel_delete_error(
    mocker, mock_logger, emailModel_with_filepaths, mock_os_remove
):
    """Tests :func:`core.models.EMailModel.EMailModel.delete`
    if delete throws an exception.
    """
    mock_delete = mocker.patch(
        "core.models.EMailModel.models.Model.delete",
        autospec=True,
        side_effect=AssertionError,
    )

    with pytest.raises(AssertionError):
        emailModel_with_filepaths.delete()

    mock_delete.assert_called_once()
    mock_os_remove.assert_not_called()
    mock_logger.debug.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("save_to_eml, expectedCall", [(True, 1), (False, 0)])
def test_save_data_settings(
    emailModel,
    mock_message,
    spy_Model_save,
    mock_EMailModel_save_to_storage,
    mock_EMailModel_render_to_storage,
    save_to_eml,
    expectedCall,
):
    emailModel.mailbox.save_toEML = save_to_eml

    emailModel.save(emailData=mock_message)

    spy_Model_save.assert_called_once_with(emailModel)
    assert mock_EMailModel_save_to_storage.call_count == expectedCall
    if expectedCall:
        mock_EMailModel_save_to_storage.assert_called_with(emailModel, mock_message)
    mock_EMailModel_render_to_storage.assert_called_once_with(emailModel, mock_message)


@pytest.mark.django_db
def test_save_no_data(
    emailModel,
    spy_Model_save,
    mock_EMailModel_save_to_storage,
    mock_EMailModel_render_to_storage,
):
    emailModel.mailbox.save_toEML = True

    emailModel.save()

    spy_Model_save.assert_called_once_with(emailModel)
    mock_EMailModel_save_to_storage.assert_not_called()
    mock_EMailModel_render_to_storage.assert_not_called()


@pytest.mark.django_db
def test_save_data_failure(
    emailModel,
    mock_message,
    spy_Model_save,
    mock_EMailModel_save_to_storage,
    mock_EMailModel_render_to_storage,
):
    mock_EMailModel_save_to_storage.side_effect = AssertionError
    emailModel.mailbox.save_toEML = True

    with pytest.raises(AssertionError):
        emailModel.save(emailData=mock_message)

    spy_Model_save.assert_called()
    mock_EMailModel_save_to_storage.assert_called()
    mock_EMailModel_render_to_storage.assert_not_called()


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
def test_EMailModel_isSpam(emailModel, x_spam, expectedResult):
    emailModel.x_spam = x_spam

    result = emailModel.isSpam()

    assert result is expectedResult


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_email, message_id, subject, attachments_count, correspondents_count, emailcorrespondents_count, x_spam, plain_bodytext, html_bodytext, header_count",
    TEST_EMAIL_PARAMETERS,
)
def test_EMailModel_createFromEmailBytes_success(
    override_config,
    mailboxModel,
    mock_logger,
    mock_EMailModel_save_to_storage,
    mock_EMailModel_render_to_storage,
    mock_AttachmentModel_save_to_storage,
    test_email,
    message_id,
    subject,
    attachments_count,
    correspondents_count,
    emailcorrespondents_count,
    x_spam,
    plain_bodytext,
    html_bodytext,
    header_count,
) -> None:
    with override_config(THROW_OUT_SPAM=False):
        emailModel = EMailModel.createFromEmailBytes(test_email, mailbox=mailboxModel)

    assert isinstance(emailModel, EMailModel)
    assert emailModel.message_id == message_id
    assert emailModel.email_subject == subject
    assert emailModel.x_spam == x_spam
    assert emailModel.plain_bodytext == plain_bodytext
    assert emailModel.html_bodytext == html_bodytext
    assert emailModel.attachments.count() == attachments_count
    assert emailModel.correspondents.distinct().count() == correspondents_count
    assert emailModel.correspondents.count() == emailcorrespondents_count
    assert len(emailModel.headers) == header_count
    assert emailModel.mailbox == mailboxModel
    if attachments_count > 0:
        mock_AttachmentModel_save_to_storage.assert_called()
    mock_EMailModel_save_to_storage.assert_called()
    mock_EMailModel_render_to_storage.assert_called()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
def test_EMailModel_createFromEmailBytes_duplicate(
    override_config,
    emailModel,
    mock_logger,
    mock_EMailModel_save_to_storage,
    mock_EMailModel_render_to_storage,
    mock_AttachmentModel_save_to_storage,
) -> None:
    with override_config(THROW_OUT_SPAM=False):
        result = EMailModel.createFromEmailBytes(
            f"Message-ID: {emailModel.message_id}".encode(), emailModel.mailbox
        )

    assert result is None
    mock_AttachmentModel_save_to_storage.assert_not_called()
    mock_EMailModel_save_to_storage.assert_not_called()
    mock_EMailModel_render_to_storage.assert_not_called()
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
        ("YES", False, False),
        ("NO", False, False),
    ],
)
def test_EMailModel_createFromEmailBytes_spam(
    override_config,
    mailboxModel,
    mock_logger,
    mock_EMailModel_save_to_storage,
    mock_EMailModel_render_to_storage,
    mock_AttachmentModel_save_to_storage,
    X_Spam_Flag,
    THROW_OUT_SPAM,
    expected_isNone,
) -> None:
    with override_config(THROW_OUT_SPAM=THROW_OUT_SPAM):
        result = EMailModel.createFromEmailBytes(
            f"X-Spam-Flag: {X_Spam_Flag}".encode(), mailboxModel
        )

    assert (result is None) is expected_isNone
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.exception.assert_not_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
def test_EMailModel_createFromEmailBytes_dberror(
    mocker, override_config, mailboxModel, mock_logger
) -> None:
    mock_EMailModel_save = mocker.patch(
        "core.models.EMailModel.EMailModel.save",
        autospec=True,
        side_effect=IntegrityError,
    )

    with override_config(THROW_OUT_SPAM=False):
        result = EMailModel.createFromEmailBytes(b"Message-ID: something", mailboxModel)

    assert result is None
    mock_EMailModel_save.assert_called()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.exception.assert_called()
    mock_logger.critical.assert_not_called()
