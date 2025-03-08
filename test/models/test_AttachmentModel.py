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

"""Test module for :mod:`core.models.AttachmentModel`.

Fixtures:
    :func:`fixture_attachmentModel`: Creates an :class:`core.models.AttachmentModel.AttachmentModel` instance for testing.
"""

import datetime
from email.message import Message

import pytest
from django.db import IntegrityError
from model_bakery import baker

from core.models.AttachmentModel import AttachmentModel
from core.models.EMailModel import EMailModel


@pytest.fixture(name="mock_logger", autouse=True)
def fixture_mock_logger(mocker):
    """Mocks :attr:`core.models.AttachmentModel.logger` of the module."""
    return mocker.patch("core.models.AttachmentModel.logger")


@pytest.fixture(name="mock_os_remove", autouse=True)
def fixture_mock_os_remove(mocker):
    return mocker.patch("core.models.AttachmentModel.os.remove")


@pytest.fixture(name="attachment")
def fixture_attachmentModel(faker) -> AttachmentModel:
    """Creates an :class:`core.models.AttachmentModel.AttachmentModel` owned by :attr:`owner_user`.

    Returns:
        The attachment instance for testing.
    """
    return baker.make(AttachmentModel, file_path=faker.file_path(extension="pdf"))


@pytest.mark.django_db
def test_AttachmentModel_default_creation(attachment):
    """Tests the correct default creation of :class:`core.models.AttachmentModel.AttachmentModel`."""

    assert attachment.file_name is not None
    assert isinstance(attachment.file_name, str)
    assert attachment.file_path is not None
    assert isinstance(attachment.file_path, str)
    assert attachment.datasize is not None
    assert isinstance(attachment.datasize, int)
    assert attachment.is_favorite is False
    assert attachment.email is not None
    assert isinstance(attachment.email, EMailModel)
    assert attachment.updated is not None
    assert isinstance(attachment.updated, datetime.datetime)
    assert attachment.created is not None
    assert isinstance(attachment.created, datetime.datetime)

    assert attachment.file_name in str(attachment)
    assert str(attachment.email) in str(attachment)


@pytest.mark.django_db
def test_AttachmentModel_foreign_key_deletion(attachment):
    """Tests the on_delete foreign key constraint in :class:`core.models.AttachmentModel.AttachmentModel`."""

    assert attachment is not None
    attachment.email.delete()
    with pytest.raises(AttachmentModel.DoesNotExist):
        attachment.refresh_from_db()


@pytest.mark.django_db
def test_AttachmentModel_unique():
    """Tests the unique constraints of :class:`core.models.AttachmentModel.AttachmentModel`."""

    attachment_1 = baker.make(AttachmentModel, file_path="test")
    attachment_2 = baker.make(AttachmentModel, file_path="test")
    assert attachment_1.file_path == attachment_2.file_path
    assert attachment_1.email != attachment_2.email

    email = baker.make(EMailModel, x_spam="NO")

    attachment_1 = baker.make(AttachmentModel, file_path="path_1", email=email)
    attachment_2 = baker.make(AttachmentModel, file_path="path_2", email=email)
    assert attachment_1.file_path != attachment_2.file_path
    assert attachment_1.email == attachment_2.email

    baker.make(AttachmentModel, file_path="test", email=email)
    with pytest.raises(IntegrityError):
        baker.make(AttachmentModel, file_path="test", email=email)


@pytest.mark.django_db
def test_delete_attachmentfile_success(mock_logger, attachment, mock_os_remove):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.delete`
    if the file removal is successful.
    """
    file_path = attachment.file_path

    attachment.delete()

    with pytest.raises(AttachmentModel.DoesNotExist):
        attachment.refresh_from_db()
    mock_os_remove.assert_called_with(file_path)
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("side_effect", [FileNotFoundError, OSError, Exception])
def test_delete_attachmentfile_failure(
    mock_logger, attachment, mock_os_remove, side_effect
):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.delete`
    if the file removal throws an exception.
    """
    mock_os_remove.side_effect = side_effect
    file_path = attachment.file_path

    attachment.delete()

    mock_os_remove.assert_called_with(file_path)
    with pytest.raises(AttachmentModel.DoesNotExist):
        attachment.refresh_from_db()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.exception.assert_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
def test_delete_attachmentfile_delete_error(mocker, mock_logger, attachment):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.delete`
    if delete throws an exception.
    """
    mock_delete = mocker.patch(
        "core.models.AttachmentModel.models.Model.delete", side_effect=ValueError
    )
    mock_os_remove = mocker.patch("core.models.AttachmentModel.os.remove")

    with pytest.raises(ValueError):
        attachment.delete()

    mock_delete.assert_called_once()
    mock_os_remove.assert_not_called()
    mock_logger.debug.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("save_attachments, expectedCalls", [(True, 1), (False, 0)])
def test_save_data_settings(mocker, attachment, save_attachments, expectedCalls):
    mock_super_save = mocker.patch("core.models.AttachmentModel.models.Model.save")
    mock_save_to_storage = mocker.patch(
        "core.models.AttachmentModel.AttachmentModel.save_to_storage"
    )
    attachment.email.mailbox.save_attachments = save_attachments
    mock_data = mocker.MagicMock(spec=Message)

    attachment.save(attachmentData=mock_data)

    assert mock_save_to_storage.call_count == expectedCalls
    mock_super_save.assert_called()


@pytest.mark.django_db
def test_save_no_data(mocker, attachment):
    mock_super_save = mocker.patch("core.models.AttachmentModel.models.Model.save")
    mock_save_to_storage = mocker.patch(
        "core.models.AttachmentModel.AttachmentModel.save_to_storage"
    )
    attachment.email.mailbox.save_attachments = True

    attachment.save()

    mock_super_save.assert_called_once_with()
    mock_save_to_storage.assert_not_called()


@pytest.mark.django_db
def test_save_data_failure(mocker, attachment):
    mock_super_save = mocker.patch("core.models.AttachmentModel.models.Model.save")
    mock_save_to_storage = mocker.patch(
        "core.models.AttachmentModel.AttachmentModel.save_to_storage",
        side_effect=AssertionError,
    )
    attachment.email.mailbox.save_attachments = True
    mock_data = mocker.MagicMock(spec=Message)

    with pytest.raises(AssertionError):
        attachment.save(attachmentData=mock_data)

    mock_super_save.assert_called()
    mock_save_to_storage.assert_called()


@pytest.mark.django_db
def test_fromData(mocker):
    mock_data = mocker.MagicMock(spec=Message)

    result = AttachmentModel.fromData(mock_data, None)

    mock_data.get_filename.assert_called_once_with()
    mock_data.as_bytes.assert_called_once_with()
    mock_data.as_bytes.return_value.__len__.assert_called_once()
    assert isinstance(result, AttachmentModel)
    assert result.file_name == mock_data.get_filename.return_value
    assert result.datasize == mock_data.as_bytes.return_value.__len__.return_value
