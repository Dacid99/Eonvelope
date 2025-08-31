# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
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

"""Test module for :mod:`core.signals.delete_Email`."""

import pytest
from django.core.files.storage import default_storage

from core.models import Email


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """The mocked :attr:`core.signals.delete_Email.logger`."""
    return mocker.patch("core.signals.delete_Email.logger", autospec=True)


@pytest.mark.django_db
def test_delete_email_no_file(fake_email, mock_logger):
    """Test individual deletion of an :class:`core.models.Email` instance
    in case its `eml_filepath` is not set.
    """
    assert not fake_email.eml_filepath

    fake_email.delete()

    with pytest.raises(Email.DoesNotExist):
        fake_email.refresh_from_db()

    mock_logger.debug.assert_not_called()


@pytest.mark.django_db
def test_delete_email_with_file(fake_email_with_file, mock_logger):
    """Test individual deletion of an :class:`core.models.Email` instance
    in case its `eml_filepath` is set.
    """
    assert default_storage.exists(fake_email_with_file.eml_filepath)

    fake_email_with_file.delete()

    assert not default_storage.exists(fake_email_with_file.eml_filepath)
    with pytest.raises(Email.DoesNotExist):
        fake_email_with_file.refresh_from_db()

    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_cascade_delete_email_with_file(
    fake_email_with_file, fake_mailbox, mock_logger
):
    """Test cascade deletion of an :class:`core.models.Email` instance
    in case its `eml_filepath` is set.
    """
    assert default_storage.exists(fake_email_with_file.eml_filepath)

    fake_mailbox.delete()

    assert not default_storage.exists(fake_email_with_file.eml_filepath)
    with pytest.raises(Email.DoesNotExist):
        fake_email_with_file.refresh_from_db()

    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_bulk_delete_email_with_file(fake_email_with_file, mock_logger):
    """Test bulk deletion of an :class:`core.models.Email` instance
    in case its `eml_filepath` is not set.
    """
    assert default_storage.exists(fake_email_with_file.eml_filepath)

    Email.objects.all().delete()

    assert not default_storage.exists(fake_email_with_file.eml_filepath)
    with pytest.raises(Email.DoesNotExist):
        fake_email_with_file.refresh_from_db()

    mock_logger.debug.assert_called()
