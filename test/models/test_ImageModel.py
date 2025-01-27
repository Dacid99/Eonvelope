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


"""Test module for :mod:`core.models.ImageModel`.

Fixtures:
    :func:`fixture_imageModel`: Creates an :class:`core.models.ImageModel.ImageModel` instance for testing.
"""

import datetime

import pytest
from django.db import IntegrityError
from faker import Faker
from model_bakery import baker

from core.models.EMailModel import EMailModel
from core.models.ImageModel import ImageModel


@pytest.fixture(name='mock_logger', autouse=True)
def fixture_mock_logger(mocker):
    """Mocks :attr:`core.models.ImageModel.logger` of the module."""
    return mocker.patch('core.models.ImageModel.logger')


@pytest.fixture(name='image')
def fixture_imageModel() -> ImageModel:
    """Creates an :class:`core.models.ImageModel.ImageModel` instance for testing.


    Returns:
        The image instance for testing.
    """
    return baker.make(
        ImageModel,
        file_path=Faker().file_path(extension='pdf')
    )


@pytest.mark.django_db
def test_ImageModel_creation(image):
    """Tests the correct default creation of :class:`core.models.ImageModel.ImageModel`."""

    assert image.file_name is not None
    assert isinstance(image.file_name, str)
    assert image.file_path is not None
    assert isinstance(image.file_path, str)
    assert image.datasize is not None
    assert isinstance(image.datasize, int)
    assert image.is_favorite is False
    assert image.email is not None
    assert isinstance(image.email, EMailModel)
    assert image.updated is not None
    assert isinstance(image.updated, datetime.datetime)
    assert image.created is not None
    assert isinstance(image.created, datetime.datetime)

    assert image.file_name in str(image)
    assert str(image.email) in str(image)


@pytest.mark.django_db
def test_ImageModel_foreign_key_deletion(image):
    """Tests the on_delete foreign key constraint in :class:`core.models.ImageModel.ImageModel`."""

    assert image is not None
    image.email.delete()
    with pytest.raises(ImageModel.DoesNotExist):
        image.refresh_from_db()


@pytest.mark.django_db
def test_ImageModel_unique():
    """Tests the unique constraints of :class:`core.models.ImageModel.ImageModel`."""

    image_1 = baker.make(ImageModel, file_path="test")
    image_2 = baker.make(ImageModel, file_path="test")
    assert image_1.file_path == image_2.file_path
    assert image_1.email != image_2.email

    email = baker.make(EMailModel)

    image_1 = baker.make(ImageModel, file_path="path_1", email = email)
    image_2 = baker.make(ImageModel, file_path="path_2", email = email)
    assert image_1.file_path != image_2.file_path
    assert image_1.email == image_2.email

    baker.make(ImageModel, file_path="test", email = email)
    with pytest.raises(IntegrityError):
        baker.make(ImageModel, file_path="test", email = email)


@pytest.mark.django_db
def test_delete_imagefile_success(mocker, mock_logger, image):
    """Tests :func:`core.models.ImageModel.ImageModel.delete`
    if the file removal is successful.
    """
    mock_os_remove = mocker.patch('core.models.ImageModel.os.remove')
    file_path = image.file_path

    image.delete()

    with pytest.raises(ImageModel.DoesNotExist):
        image.refresh_from_db()
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
def test_delete_imagefile_failure(mocker, image, mock_logger, side_effect):
    """Tests :func:`core.models.ImageModel.ImageModel.delete`
    if the file removal throws an exception.
    """
    mock_os_remove = mocker.patch('core.models.ImageModel.os.remove', side_effect=side_effect)
    file_path = image.file_path

    image.delete()

    mock_os_remove.assert_called_with(file_path)
    with pytest.raises(ImageModel.DoesNotExist):
        image.refresh_from_db()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_called()
    mock_logger.critical.assert_not_called()
