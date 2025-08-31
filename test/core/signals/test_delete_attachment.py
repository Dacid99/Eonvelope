# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Attachmentkasten - a open-source self-hostable attachment archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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

"""Test module for :mod:`core.signals.delete_Attachment`."""

import pytest
from django.core.files.storage import default_storage

from core.models import Attachment


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """The mocked :attr:`core.signals.delete_Attachment.logger`."""
    return mocker.patch("core.signals.delete_Attachment.logger", autospec=True)


@pytest.mark.django_db
def test_delete_attachment_no_file(fake_attachment, mock_logger):
    """Test individual deletion of an :class:`core.models.Attachment` instance
    in case its `file_path` is not set.
    """
    assert not fake_attachment.file_path

    fake_attachment.delete()

    with pytest.raises(Attachment.DoesNotExist):
        fake_attachment.refresh_from_db()

    mock_logger.debug.assert_not_called()


@pytest.mark.django_db
def test_delete_attachment_with_file(fake_attachment_with_file, mock_logger):
    """Test individual deletion of an :class:`core.models.Attachment` instance
    in case its `file_path` is set.
    """
    assert default_storage.exists(fake_attachment_with_file.file_path)

    fake_attachment_with_file.delete()

    assert not default_storage.exists(fake_attachment_with_file.file_path)
    with pytest.raises(Attachment.DoesNotExist):
        fake_attachment_with_file.refresh_from_db()

    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_cascade_delete_attachment_with_file(
    fake_attachment_with_file, fake_mailbox, mock_logger
):
    """Test cascade deletion of an :class:`core.models.Attachment` instance
    in case its `file_path` is set.
    """
    assert default_storage.exists(fake_attachment_with_file.file_path)

    fake_mailbox.delete()

    assert not default_storage.exists(fake_attachment_with_file.file_path)
    with pytest.raises(Attachment.DoesNotExist):
        fake_attachment_with_file.refresh_from_db()

    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_bulk_delete_attachment_with_file(fake_attachment_with_file, mock_logger):
    """Test bulk deletion of an :class:`core.models.Attachment` instance
    in case its `file_path` is not set.
    """
    assert default_storage.exists(fake_attachment_with_file.file_path)

    Attachment.objects.all().delete()

    assert not default_storage.exists(fake_attachment_with_file.file_path)
    with pytest.raises(Attachment.DoesNotExist):
        fake_attachment_with_file.refresh_from_db()

    mock_logger.debug.assert_called()
