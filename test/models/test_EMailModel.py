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

import pytest
from django.db import IntegrityError
from faker import Faker
from model_bakery import baker

from core.models.AccountModel import AccountModel
from core.models.EMailModel import EMailModel
from core.models.MailingListModel import MailingListModel


@pytest.fixture(name='mock_logger', autouse=True)
def fixture_mock_logger(mocker):
    """Mocks :attr:`core.models.EMailModel.logger` of the module."""
    return mocker.patch('core.models.EMailModel.logger')


@pytest.fixture(name='email')
def fixture_emailModel() -> EMailModel:
    """Creates an :class:`core.models.EMailModel.EMailModel`.

    Returns:
        The email instance for testing.
    """
    return baker.make(EMailModel)

@pytest.mark.django_db
def test_EMailModel_creation(email):
    """Tests the correct default creation of :class:`core.models.EMailModel.EMailModel`."""

    assert email.message_id is not None
    assert isinstance(email.message_id, str)
    assert email.datetime is not None
    assert isinstance(email.datetime, datetime.datetime)
    assert email.email_subject is not None
    assert isinstance(email.email_subject, str)
    assert email.bodytext is not None
    assert isinstance(email.bodytext, str)
    assert email.inReplyTo is None
    assert email.datasize is not None
    assert isinstance(email.datasize, int)
    assert email.eml_filepath is None
    assert email.prerender_filepath is None
    assert email.is_favorite is False

    assert email.mailinglist is None
    assert email.account is not None
    assert isinstance(email.account, AccountModel)
    assert email.comments is None
    assert email.keywords is None
    assert email.importance is None
    assert email.priority is None
    assert email.precedence is None
    assert email.received is None
    assert email.user_agent is None
    assert email.auto_submitted is None
    assert email.content_type is None
    assert email.content_language is None
    assert email.content_location is None
    assert email.x_priority is None
    assert email.x_originated_client is None
    assert email.x_spam is None

    assert isinstance(email.updated, datetime.datetime)
    assert email.updated is not None
    assert isinstance(email.created, datetime.datetime)
    assert email.created is not None

    assert email.message_id in str(email)
    assert str(email.datetime) in str(email)
    assert email.email_subject in str(email)
    assert str(email.account) in str(email)


@pytest.mark.django_db
def test_EMailModel_foreign_key_account_deletion(email):
    """Tests the on_delete foreign key constraint on account in :class:`core.models.EMailModel.EMailModel`."""

    email.account.delete()

    with pytest.raises(EMailModel.DoesNotExist):
        email.refresh_from_db()


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

    email_1 = baker.make(EMailModel, message_id="abc123")
    email_2 = baker.make(EMailModel, message_id="abc123")
    assert email_1.message_id == email_2.message_id
    assert email_1.account != email_2.account

    account = baker.make(AccountModel)

    email_1 = baker.make(EMailModel, account = account)
    email_2 = baker.make(EMailModel, account = account)
    assert email_1.message_id != email_2.message_id
    assert email_1.account == email_2.account

    baker.make(EMailModel, message_id="abc123", account = account)
    with pytest.raises(IntegrityError):
        baker.make(EMailModel, message_id="abc123", account = account)


@pytest.mark.django_db
def test_post_delete_email_success(mocker, mock_logger, email):
    """Tests :func:`core.models.EMailModel.EMailModel.delete`
    if the file removal is successful.
    """
    mock_os_remove = mocker.patch('core.models.EMailModel.os.remove')
    email.eml_filepath = Faker().file_path(extension='eml')
    email.prerender_filepath = Faker().file_path(extension='png')
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
    'side_effects',
    [
        [Exception, None],
        [None, Exception],
        [Exception, Exception],
    ]
)
def test_post_delete_email_failure(mocker, email, mock_logger, side_effects):
    """Tests :func:`core.models.EMailModel.EMailModel.delete`
    if the file removal throws an exception.
    """
    mock_os_remove = mocker.patch('core.models.EMailModel.os.remove', side_effect=side_effects)
    email.eml_filepath = Faker().file_path(extension='eml')
    email.prerender_filepath = Faker().file_path(extension='png')
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
