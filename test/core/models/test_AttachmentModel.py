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
import os

import pytest
from django.db import IntegrityError
from django.urls import reverse
from model_bakery import baker

import core.models.AttachmentModel
from core.models.AttachmentModel import AttachmentModel
from core.models.EMailModel import EMailModel


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Fixture mocking the logger :attr:`core.models.AttachmentModel.logger` of the module."""
    return mocker.patch("core.models.AttachmentModel.logger", autospec=True)


@pytest.fixture
def mock_open(mocker, fake_file_bytes):
    """Fixture to mock the builtin :func:`open`."""
    mock_open = mocker.mock_open(read_data=fake_file_bytes)
    mocker.patch("core.utils.fileManagment.open", mock_open)
    return mock_open


@pytest.fixture(autouse=True)
def mock_os_remove(mocker):
    """Fixture mocking :func:`os.remove`."""
    return mocker.patch("core.models.AttachmentModel.os.remove", autospec=True)


@pytest.fixture
def mock_StorageModel_getSubdirectory(mocker, faker):
    fake_directory_path = os.path.dirname(faker.file_path())
    mock_StorageModel_getSubdirectory = mocker.patch(
        "core.models.StorageModel.StorageModel.getSubdirectory", autospec=True
    )
    mock_StorageModel_getSubdirectory.return_value = fake_directory_path
    return mock_StorageModel_getSubdirectory


@pytest.fixture
def mock_AttachmentModel_save_to_storage(mocker):
    return mocker.patch(
        "core.models.AttachmentModel.AttachmentModel.save_to_storage", autospec=True
    )


@pytest.fixture
def spy_Model_save(mocker):
    return mocker.spy(core.models.AttachmentModel.models.Model, "save")


@pytest.mark.django_db
def test_AttachmentModel_fields(attachmentModel):
    """Tests the fields of :class:`core.models.AttachmentModel.AttachmentModel`."""

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


@pytest.mark.django_db
def test_AttachmentModel___str__(attachmentModel):
    """Tests the string representation of :class:`core.models.AttachmentModel.AttachmentModel`."""
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
def test_AttachmentModel_unique_constraints():
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
def test_AttachmentModel_delete_attachmentfile_success(
    attachmentModel, mock_logger, mock_os_remove
):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.delete`
    in case the file removal is successful.
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
def test_AttachmentModel_delete_attachmentfile_failure(
    attachmentModel, mock_logger, mock_os_remove, side_effect
):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.delete`
    in case the file removal raises an exception.
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
def test_AttachmentModel_delete_attachmentfile_delete_error(
    mocker,
    attachmentModel,
    mock_logger,
    mock_os_remove,
):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.delete`
    in case delete raises an exception.
    """
    mock_delete = mocker.patch(
        "core.models.AttachmentModel.models.Model.delete",
        autospec=True,
        side_effect=AssertionError,
    )

    with pytest.raises(AssertionError):
        attachmentModel.delete()

    mock_delete.assert_called_once()
    mock_os_remove.assert_not_called()
    mock_logger.debug.assert_not_called()


@pytest.mark.django_db
def test_save_to_storage_success(
    faker,
    mock_message,
    attachmentModel,
    mock_logger,
    mock_open,
    mock_StorageModel_getSubdirectory,
):
    fake_message_payload = faker.text().encode()
    mock_message.get_payload.return_value = fake_message_payload
    attachmentModel.file_path = None

    attachmentModel.save_to_storage(mock_message)

    mock_StorageModel_getSubdirectory.assert_called_once_with(
        attachmentModel.email.message_id
    )
    mock_open.assert_called_once_with(
        os.path.join(
            mock_StorageModel_getSubdirectory.return_value, attachmentModel.file_name
        ),
        "wb",
    )
    mock_open.return_value.write.assert_called_once_with(fake_message_payload)
    attachmentModel.refresh_from_db()
    assert attachmentModel.file_path == os.path.join(
        mock_StorageModel_getSubdirectory.return_value, attachmentModel.file_name
    )
    mock_logger.debug.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_save_to_storage_file_path_set(
    faker,
    mock_message,
    attachmentModel,
    mock_logger,
    mock_open,
    mock_StorageModel_getSubdirectory,
):
    fake_message_payload = faker.text().encode()
    mock_message.get_payload.return_value = fake_message_payload
    previous_file_path = attachmentModel.file_path

    attachmentModel.save_to_storage(mock_message)

    mock_StorageModel_getSubdirectory.assert_not_called()
    mock_open.assert_not_called()
    attachmentModel.refresh_from_db()
    assert attachmentModel.file_path == previous_file_path
    mock_logger.debug.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_save_to_storage_open_osError(
    faker,
    mock_message,
    attachmentModel,
    mock_logger,
    mock_open,
    mock_StorageModel_getSubdirectory,
):
    fake_message_payload = faker.text().encode()
    mock_message.get_payload.return_value = fake_message_payload
    attachmentModel.file_path = None
    mock_open.side_effect = OSError

    attachmentModel.save_to_storage(mock_message)

    mock_StorageModel_getSubdirectory.assert_called_once_with(
        attachmentModel.email.message_id
    )
    mock_open.assert_called_once_with(
        os.path.join(
            mock_StorageModel_getSubdirectory.return_value, attachmentModel.file_name
        ),
        "wb",
    )
    mock_open.return_value.write.assert_not_called()
    assert attachmentModel.file_path is None
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_save_to_storage_write_osError(
    faker,
    mock_message,
    attachmentModel,
    mock_logger,
    mock_open,
    mock_StorageModel_getSubdirectory,
):
    fake_message_payload = faker.text().encode()
    mock_message.get_payload.return_value = fake_message_payload
    attachmentModel.file_path = None
    mock_open.return_value.write.side_effect = OSError

    attachmentModel.save_to_storage(mock_message)

    mock_StorageModel_getSubdirectory.assert_called_once_with(
        attachmentModel.email.message_id
    )
    mock_open.assert_called_once_with(
        os.path.join(
            mock_StorageModel_getSubdirectory.return_value, attachmentModel.file_name
        ),
        "wb",
    )
    mock_open.return_value.write.assert_called_once_with(fake_message_payload)
    assert attachmentModel.file_path is None
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("save_attachments, expectedCalls", [(True, 1), (False, 0)])
def test_AttachmentModel_save_with_data_success(
    attachmentModel,
    mock_message,
    mock_AttachmentModel_save_to_storage,
    spy_Model_save,
    save_attachments,
    expectedCalls,
):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.save`
    in case of success with data to be saved.
    """
    attachmentModel.email.mailbox.save_attachments = save_attachments

    attachmentModel.save(attachmentData=mock_message)

    assert mock_AttachmentModel_save_to_storage.call_count == expectedCalls
    spy_Model_save.assert_called()


@pytest.mark.django_db
def test_AttachmentModel_save_no_data(
    attachmentModel, mock_AttachmentModel_save_to_storage, spy_Model_save
):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.save`
    in case of success without data to be saved.
    """
    attachmentModel.email.mailbox.save_attachmentModels = True

    attachmentModel.save()

    spy_Model_save.assert_called_once_with(attachmentModel)
    mock_AttachmentModel_save_to_storage.assert_not_called()


@pytest.mark.django_db
def test_AttachmentModel_save_with_data_failure(
    attachmentModel, mock_message, mock_AttachmentModel_save_to_storage, spy_Model_save
):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.save`
    in case of the data fails to be saved.
    """
    mock_AttachmentModel_save_to_storage.side_effect = AssertionError
    attachmentModel.email.mailbox.save_attachmentModels = True

    with pytest.raises(AssertionError):
        attachmentModel.save(attachmentData=mock_message)

    spy_Model_save.assert_called()
    mock_AttachmentModel_save_to_storage.assert_called()


@pytest.mark.django_db
def test_AttachmentModel_fromData(mock_message):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.fromData`
    in case of success.
    """
    result = AttachmentModel.fromData(mock_message, None)

    mock_message.get_filename.assert_called_once_with()
    mock_message.as_bytes.assert_called_once_with()
    mock_message.as_bytes.return_value.__len__.assert_called_once()
    assert isinstance(result, AttachmentModel)
    assert result.file_name == mock_message.get_filename.return_value
    assert result.datasize == mock_message.as_bytes.return_value.__len__.return_value


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_path, expected_has_download",
    [
        (None, False),
        ("some/file/path", True),
    ],
)
def test_AttachmentModel_has_download(
    attachmentModel, file_path, expected_has_download
):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.has_download` in the two relevant cases."""
    attachmentModel.file_path = file_path

    result = attachmentModel.has_download

    assert result == expected_has_download


@pytest.mark.django_db
@pytest.mark.parametrize(
    "content_type, expected_has_thumbnail",
    [
        ("", False),
        ("oo4vuy0s9yn/qwytrhrfvb9", False),
        ("image/something", True),
        ("video/whatever", False),
        ("application/pdf", False),
    ],
)
def test_AttachmentModel_has_thumbnail(
    attachmentModel, content_type, expected_has_thumbnail
):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.has_thumbnail` in the two relevant cases."""
    attachmentModel.content_type = content_type

    result = attachmentModel.has_thumbnail

    assert result == expected_has_thumbnail


@pytest.mark.django_db
def test_AttachmentModel_get_absolute_thumbnail_url(attachmentModel):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.get_absolute_thumbnail_url`."""
    result = attachmentModel.get_absolute_thumbnail_url()

    assert result == reverse(
        f"api:v1:{attachmentModel.BASENAME}-download",
        kwargs={"pk": attachmentModel.pk},
    )


@pytest.mark.django_db
def test_AttachmentModel_get_absolute_url(attachmentModel):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.get_absolute_url`."""
    result = attachmentModel.get_absolute_url()

    assert result == reverse(
        f"web:{attachmentModel.BASENAME}-detail",
        kwargs={"pk": attachmentModel.pk},
    )


@pytest.mark.django_db
def test_AttachmentModel_get_absolute_list_url(attachmentModel):
    """Tests :func:`core.models.AttachmentModel.AttachmentModel.get_absolute_list_url`."""
    result = attachmentModel.get_absolute_list_url()

    assert result == reverse(f"web:{attachmentModel.BASENAME}-filter-list")
