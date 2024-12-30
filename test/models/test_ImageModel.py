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


"""Test module for :mod:`Emailkasten.Models.ImageModel`.

Fixtures:
    :func:`fixture_imageModel`: Creates an :class:`Emailkasten.Models.ImageModel.ImageModel` instance for testing.
"""

import datetime

import pytest
from django.db import IntegrityError
from faker import Faker
from model_bakery import baker

from Emailkasten.Models.EMailModel import EMailModel
from Emailkasten.Models.ImageModel import ImageModel


@pytest.fixture(name='image')
def fixture_imageModel() -> ImageModel:
    """Creates an :class:`Emailkasten.Models.ImageModel.ImageModel` instance for testing.


    Returns:
        The image instance for testing.
    """
    return baker.make(
        ImageModel,
        file_path=Faker().file_path(extension='pdf')
    )


@pytest.mark.django_db
def test_ImageModel_creation(image):
    """Tests the correct default creation of :class:`Emailkasten.Models.ImageModel.ImageModel`."""

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
    """Tests the on_delete foreign key constraint in :class:`Emailkasten.Models.ImageModel.ImageModel`."""

    assert image is not None
    image.email.delete()
    with pytest.raises(ImageModel.DoesNotExist):
        image.refresh_from_db()


@pytest.mark.django_db
def test_ImageModel_unique():
    """Tests the unique constraints of :class:`Emailkasten.Models.ImageModel.ImageModel`."""

    image_1 = baker.make(ImageModel, file_path="test")
    image_2 = baker.make(ImageModel, file_path="test")
    assert image_1.file_path == image_2.file_path
    assert image_1.email != image_2.email

    email = baker.make(EMailModel)

    image_1 = baker.make(ImageModel, email = email)
    image_2 = baker.make(ImageModel, email = email)
    assert image_1.file_path != image_2.file_path
    assert image_1.email == image_2.email

    baker.make(ImageModel, file_path="test", email = email)
    with pytest.raises(IntegrityError):
        baker.make(ImageModel, file_path="test", email = email)
