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

"""Test file for :mod:`Emailkasten.signals.delete_AttachmentModel`."""

import pytest

from Emailkasten.Models.AttachmentModel import AttachmentModel

from ..models.test_AttachmentModel import fixture_attachmentModel


@pytest.fixture(name='mock_logger', autouse=True)
def fixture_mock_logger(mocker):
    """Mocks :attr:`Emailkasten.signals.delete_AttachmentModel.logger` of the module."""
    return mocker.patch('Emailkasten.signals.delete_AttachmentModel.logger')

@pytest.mark.django_db
def test_post_delete_attachment_success(mocker, mock_logger, attachment):
    """Tests :func:`Emailkasten.signals.deleteAttachmentModel.post_delete_attachment`
    if the file removal is successful.
    """
    mock_os_remove = mocker.patch('Emailkasten.signals.delete_AttachmentModel.os.remove')
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
@pytest.mark.parametrize(
    'side_effect',
    [
        FileNotFoundError,
        OSError,
        Exception
    ]
)
def test_post_delete_attachment_failure(mocker, attachment, mock_logger, side_effect):
    """Tests :func:`Emailkasten.signals.deleteAttachmentModel.post_delete_attachment`
    if the file removal throws an exception.
    """
    mock_os_remove = mocker.patch('Emailkasten.signals.delete_AttachmentModel.os.remove', side_effect=side_effect)
    file_path = attachment.file_path

    attachment.delete()

    mock_os_remove.assert_called_with(file_path)
    with pytest.raises(AttachmentModel.DoesNotExist):
        attachment.refresh_from_db()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_called()
    mock_logger.critical.assert_not_called()
