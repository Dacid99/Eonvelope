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

"""Test module for the :class:`core.backends.ShardedFilesystemStorage` storage class."""

import os
from io import BytesIO

import pytest
from django.core.files.storage import default_storage

from core.models import StorageShard


@pytest.fixture(autouse=True)
def always_fake_fs(fake_fs):
    """The following tests all run against a mocked fs."""


@pytest.mark.django_db
def test_ShardedFileSystemStorage_save_single(faker, fake_file):
    fake_name = faker.name()
    assert StorageShard.objects.count() == 0
    assert default_storage.listdir("")[0] == []
    assert default_storage.listdir("")[1] == []

    result = default_storage.save(fake_name, fake_file)

    assert StorageShard.objects.count() == 1
    storage = StorageShard.objects.first()
    assert storage.file_count == 1
    assert os.path.dirname(result) == str(storage.shard_directory_name)
    assert default_storage.listdir("")[0] == [os.path.dirname(result)]
    assert default_storage.listdir("")[1] == []
    assert default_storage.listdir(os.path.dirname(result))[0] == []
    assert default_storage.listdir(os.path.dirname(result))[1] == [
        os.path.basename(result)
    ]
    assert default_storage.open(result).read() == fake_file.getvalue()


@pytest.mark.django_db
@pytest.mark.override_config(STORAGE_MAX_FILES_PER_DIR=3)
def test_ShardedFileSystemStorage_save_multi(faker, fake_file):
    assert StorageShard.objects.count() == 0
    assert default_storage.listdir("")[0] == []
    assert default_storage.listdir("")[1] == []

    for index in range(2 * 3 + 2):
        default_storage.save(faker.name() + str(index), fake_file)

    assert StorageShard.objects.count() == 3
    storage = StorageShard.objects.get(current=True)
    assert storage.file_count == 2
    assert len(default_storage.listdir("")[0]) == 3
    assert len(default_storage.listdir("")[1]) == 0


@pytest.mark.django_db
@pytest.mark.parametrize("unsafe_name", ["t/1", "*a*", "2.3", "~3", "<id/numbers>"])
def test_ShardedFileSystemStorage_save_unsafe_name(fake_file, unsafe_name):
    assert StorageShard.objects.count() == 0

    result = default_storage.save(unsafe_name, fake_file)

    assert StorageShard.objects.count() == 1
    storage = StorageShard.objects.first()
    assert storage.file_count == 1
    assert os.path.dirname(result) == str(storage.shard_directory_name)
    assert "/" not in os.path.basename(result)
    assert "~" not in os.path.basename(result)
