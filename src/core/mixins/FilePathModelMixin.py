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

"""Module with the :class:`core.mixins.FilePathModelMixin` mixin."""

import logging
from io import BytesIO
from typing import Any, override

from django.core.files import File
from django.core.files.storage import default_storage
from django.db.models import CharField, Model
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)


class FilePathModelMixin(Model):
    """Mixin adding functionality for managing a single storage file for a model class."""

    file_path = CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("filepath"),
    )
    """The relative path in the storage where the file is stored.
    Can be null if no file has been saved (null does not collide with the unique constraint.).
    """

    class Meta:
        """Metadata class for the mixin, abstract to avoid makemigrations picking it up."""

        abstract = True

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Extended :django::func:`django.models.Model.save` method.

        Saves the data to storage if configured.
        """
        file_payload = kwargs.pop("file_payload", None)
        super().save(*args, **kwargs)
        if file_payload is not None and not self.file_path:
            logger.debug("Storing file for %s ...", self)
            self.file_path = default_storage.save(
                self._get_storage_file_name(),
                BytesIO(file_payload),
            )
            self.save(update_fields=["file_path"])
            logger.debug("Successfully stored file.")

    def _get_storage_file_name(self) -> str:
        """Create the filename for the stored file."""
        return str(self.pk)

    def open_file(self, mode: str = "rb") -> File:
        """Opens and returns the stored file as a filestream.

        Note:
            Use inside a with block.

        Args:
            mode: The mode the file is opened in.

        Returns:
            The filestream of the file.

        Raises:
            FileNotFoundError: If the `file_path` is not set or the file is not found in the storage.
        """
        if not self.file_path:
            raise FileNotFoundError("File has not been stored.")
        try:
            file = default_storage.open(self.file_path, mode=mode)
        except FileNotFoundError:
            logger.exception("File for %s not found in storage!", self)
            raise
        return file

    def delete_file(self) -> None:
        """Deletes the file and sets `file_path` to `None`.

        Intended for use in a signal.
        """
        if self.file_path:
            logger.debug("Removing file for %s from storage ...", self)
            default_storage.delete(self.file_path)
            self.file_path = None
            logger.debug("Successfully removed file from storage.")
