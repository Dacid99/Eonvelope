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
    :func:`fixture_attachmentModelModel`: Creates an :class:`core.models.AttachmentModel.AttachmentModel` instance for testing.
"""

import datetime
from email.message import Message

import pytest
from django.db import IntegrityError
from model_bakery import baker

from core.models.AttachmentModel import AttachmentModel
from core.models.EMailModel import EMailModel


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Mocks :attr:`core.models.AttachmentModel.logger` of the module."""
    return mocker.patch("core.models.AttachmentModel.logger", autospec=True)


@pytest.fixture(autouse=True)
def mock_os_remove(mocker):
    return mocker.patch("core.models.AttachmentModel.os.remove", autospec=True)


@pytest.mark.django_db
def test_AttachmentModel_default_creation(attachmentModel):
    """Tests the correct default creation of :class:`core.models.AttachmentModel.AttachmentModel`."""

    assert attachmentModel.file_name is not None
    assert isinstance(attachmentModel.file_name, str)
    assert attachmentModel.file_path is not None
    assert isinstance(attachmentModel.file_path, str)
    assert attachmentModel.datasize is not None
    assert isinstance(attachmentModel.datasize, int)
    assert attachmentModel.is_favorite is False
    assert attachmentModel.email is not None
    assert isinstance(attachmentModel.email, EMailModel)
    assert attachmentModel.updated is not None
    assert isinstance(attachmentModel.updated, datetime.datetime)
    assert attachmentModel.created is not None
    assert isinstance(attachmentModel.created, datetime.datetime)

    assert attachmentModel.file_name in str(attachmentModel)
    assert str(attachmentModel.email) in str(attachmentModel)


@pytest.mark.django_db
def test_AttachmentModel_foreign_key_deletion(attachmentModel):
    """Tests the on_delete foreign key constraint in :class:`core.models.AttachmentModel.AttachmentModel`."""

    assert attachmentModel is not None
    attachmentModel.email.delete()
    with pytest.raises(AttachmentModel.DoesNotExist):
        attachmentModel.refresh_from_db()


@pytest.mark.django_db
def test_AttachmentModel_unique():
    """Tests the unique constraints of :class:`core.models.AttachmentModel.AttachmentModel`."""

    attachmentModel_1 = baker.make(AttachmentModel, file_path="test")
    attachmentModel_2 = baker.make(AttachmentModel, file_path="test")
    assert attachmentModel_1.file_path == attachmentModel_2.file_path
    assert attachmentModel_1.email != attachmentModel_2.email

    email = baker.make(EMailModel, x_spam="NO")

    attachmentModel_1 = baker.make(AttachmentModel, file_path="path_1", email=email)
    attachmentModel_2 = baker.make(AttachmentModel, file_path="path_2", email=email)
    assert attachmentModel_1.file_path != attachmentModel_2.file_path
    assert attachmentModel_1.email == attachmentModel_2.email

    baker.make(AttachmentModel, file_path="test", email=email)
    with pytest.raises(IntegrityError):
        baker.make(AttachmentModel, file_path="test", email=email)


@pytest.mark.django_db
def test_delete_attachmentModelfile_success(
    mock_logger, attachmentModel, mock_os_remove
):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.delete`
    if the file removal is successful.
    """
    file_path = attachmentModel.file_path

    attachmentModel.delete()

    with pytest.raises(AttachmentModel.DoesNotExist):
        attachmentModel.refresh_from_db()
    mock_os_remove.assert_called_with(file_path)
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("side_effect", [FileNotFoundError, OSError, Exception])
def test_delete_attachmentModelfile_failure(
    mock_logger, attachmentModel, mock_os_remove, side_effect
):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.delete`
    if the file removal throws an exception.
    """
    mock_os_remove.side_effect = side_effect
    file_path = attachmentModel.file_path

    attachmentModel.delete()

    mock_os_remove.assert_called_with(file_path)
    with pytest.raises(AttachmentModel.DoesNotExist):
        attachmentModel.refresh_from_db()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.exception.assert_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
def test_delete_attachmentModelfile_delete_error(
    mocker, mock_logger, mock_os_remove, attachmentModel
):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.delete`
    if delete throws an exception.
    """
    mock_delete = mocker.patch(
        "core.models.AttachmentModel.models.Model.delete",
        autospec=True,
        side_effect=ValueError,
    )

    with pytest.raises(ValueError):
        attachmentModel.delete()

    mock_delete.assert_called_once()
    mock_os_remove.assert_not_called()
    mock_logger.debug.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("save_attachments, expectedCalls", [(True, 1), (False, 0)])
def test_save_data_settings(mocker, attachmentModel, save_attachments, expectedCalls):
    mock_super_save = mocker.patch(
        "core.models.AttachmentModel.models.Model.save", autospec=True
    )
    mock_save_to_storage = mocker.patch(
        "core.models.AttachmentModel.AttachmentModel.save_to_storage", autospec=True
    )
    attachmentModel.email.mailbox.save_attachments = save_attachments
    mock_data = mocker.MagicMock(spec=Message)

    attachmentModel.save(attachmentData=mock_data)

    assert mock_save_to_storage.call_count == expectedCalls
    mock_super_save.assert_called()


@pytest.mark.django_db
def test_save_no_data(mocker, attachmentModel):
    mock_super_save = mocker.patch(
        "core.models.AttachmentModel.models.Model.save", autospec=True
    )
    mock_save_to_storage = mocker.patch(
        "core.models.AttachmentModel.AttachmentModel.save_to_storage", autospec=True
    )
    attachmentModel.email.mailbox.save_attachmentModels = True

    attachmentModel.save()

    mock_super_save.assert_called_once_with(attachmentModel)
    mock_save_to_storage.assert_not_called()


@pytest.mark.django_db
def test_save_data_failure(mocker, attachmentModel):
    mock_super_save = mocker.patch(
        "core.models.AttachmentModel.models.Model.save", autospec=True
    )
    mock_save_to_storage = mocker.patch(
        "core.models.AttachmentModel.AttachmentModel.save_to_storage",
        autospec=True,
        side_effect=AssertionError,
    )
    attachmentModel.email.mailbox.save_attachmentModels = True
    mock_data = mocker.MagicMock(spec=Message)

    with pytest.raises(AssertionError):
        attachmentModel.save(attachmentData=mock_data)

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
