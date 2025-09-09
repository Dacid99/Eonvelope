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

"""Test module for :mod:`core.models.Storage`."""

from __future__ import annotations

import os

import pytest
from health_check.storage.backends import DefaultFileStorageHealthCheck

from core.models import StorageShard


@pytest.fixture(autouse=True)
def always_fake_fs(fake_fs):
    """The following tests all run against a mocked fs."""


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """The mocked :attr:`core.models.Storage.logger`."""
    return mocker.patch("core.models.StorageShard.logger", autospec=True)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "is_current, expected_status_str", [(True, "Current"), (False, "Archived")]
)
def test___str__(faker, is_current, expected_status_str):
    """Tests :class:`core.models.StorageShard.__str__`
    in cases of different `is_current` states.
    """
    fake_filename = faker.file_name()

    result = str(StorageShard(current=is_current, shard_directory_name=fake_filename))

    assert expected_status_str in result
    assert fake_filename in result


@pytest.mark.django_db
def test_Storage_healthcheck_clean_storage(mock_logger):
    """Tests the healthcheck in case of a storage that has not been touched yet."""
    health = StorageShard.healthcheck()

    assert health
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
@pytest.mark.override_config(STORAGE_MAX_FILES_PER_DIR=3)
def test_Storage_healthcheck_filled_storage(settings):
    """Tests the correct initial allocation of storage by :class:`core.models.Storage.Storage`."""
    for index in range(2 * 3 + 2):
        storage = StorageShard.get_current_storage()
        with open(
            os.path.join(
                settings.STORAGE_PATH, str(storage.shard_directory_name), str(index)
            ),
            "w",
        ) as dummy_file:
            dummy_file.write("Some content")
        storage.increment_file_count()

    health = StorageShard.healthcheck()

    assert health


@pytest.mark.django_db
def test_Storage_health_check_duplicate_current(mock_logger):
    """Tests the storage healthcheck in case of a duplicate `current` directory."""
    StorageShard.get_current_storage()
    StorageShard.objects.create(current=True)

    health = StorageShard.healthcheck()

    assert not health
    mock_logger.critical.assert_called()


@pytest.mark.django_db
def test_Storage_health_check_file_in_storage_root(settings, mock_logger):
    """Tests the storage healthcheck in case of dirty storage."""
    with open(os.path.join(settings.STORAGE_PATH, "file"), "w") as dummy_file:
        dummy_file.write("Some content")

    health = StorageShard.healthcheck()

    assert not health
    mock_logger.critical.assert_called()


@pytest.mark.django_db
def test_Storage_health_check_missing_dir(settings, mock_logger):
    """Tests the storage healthcheck in case of a directory missing in the storage."""
    storage = StorageShard.get_current_storage()
    os.rmdir(os.path.join(settings.STORAGE_PATH, str(storage.shard_directory_name)))

    health = StorageShard.healthcheck()

    assert not health
    mock_logger.critical.assert_called()


@pytest.mark.django_db
def test_DefaultStorageStorageHealthCheck():
    """Tests django-healthchecks DefaultFileStorageHealthCheck
    impact on the StorageShard table.
    """
    assert StorageShard.get_current_storage().file_count == 0

    result = DefaultFileStorageHealthCheck().check_status()

    assert result is True
    assert StorageShard.get_current_storage().file_count == 0
