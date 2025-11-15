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

"""Test module for :mod:`core.signals.delete_Attachment`."""

import pytest
from django.core.files.storage import default_storage

from core.models import Attachment


@pytest.mark.django_db
def test_delete_attachment_no_file(fake_attachment):
    """Test individual deletion of an :class:`core.models.Attachment` instance
    in case its `file_path` is not set.
    """
    assert not fake_attachment.file_path

    fake_attachment.delete()

    with pytest.raises(Attachment.DoesNotExist):
        fake_attachment.refresh_from_db()


@pytest.mark.django_db
def test_delete_attachment_with_file(fake_attachment_with_file):
    """Test individual deletion of an :class:`core.models.Attachment` instance
    in case its `file_path` is set.
    """
    previous_file_path = fake_attachment_with_file.file_path

    assert default_storage.exists(previous_file_path)

    fake_attachment_with_file.delete()

    assert not default_storage.exists(previous_file_path)
    with pytest.raises(Attachment.DoesNotExist):
        fake_attachment_with_file.refresh_from_db()


@pytest.mark.django_db
def test_cascade_delete_attachment_with_file(fake_attachment_with_file, fake_mailbox):
    """Test cascade deletion of an :class:`core.models.Attachment` instance
    in case its `file_path` is set.
    """
    assert default_storage.exists(fake_attachment_with_file.file_path)

    fake_mailbox.delete()

    assert not default_storage.exists(fake_attachment_with_file.file_path)
    with pytest.raises(Attachment.DoesNotExist):
        fake_attachment_with_file.refresh_from_db()


@pytest.mark.django_db
def test_bulk_delete_attachment_with_file(fake_attachment_with_file):
    """Test bulk deletion of an :class:`core.models.Attachment` instance
    in case its `file_path` is not set.
    """
    assert default_storage.exists(fake_attachment_with_file.file_path)

    Attachment.objects.all().delete()

    assert not default_storage.exists(fake_attachment_with_file.file_path)
    with pytest.raises(Attachment.DoesNotExist):
        fake_attachment_with_file.refresh_from_db()
