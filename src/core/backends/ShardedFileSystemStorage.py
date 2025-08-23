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

"""Module with the :class:`core.backends.ShardedFileSystemStorage` storage class."""

import os
from typing import override

from django.core.files.storage import FileSystemStorage

from ..models import StorageShard


class ShardedFileSystemStorage(FileSystemStorage):
    """FileSystemStorage backend for sharded storage."""

    @override
    def _save(self, name: str, content: bytes) -> str:
        """Extended method for saving files in current storage directory with safe filename."""
        storage_shard = StorageShard.get_current_storage()
        name = self.generate_filename(
            os.path.join(
                str(storage_shard.shard_directory_name), name.replace("/", "_")
            )
        )
        save_return = super()._save(name, content)
        storage_shard.increment_file_count()
        return save_return

    @override
    def delete(self, name: str) -> None:
        """Extended method for deleting files in a storage directory."""
        storage_shard = StorageShard.objects.get(
            shard_directory_name=os.path.dirname(name)
        )
        super().delete(name)
        storage_shard.decrement_file_count()
