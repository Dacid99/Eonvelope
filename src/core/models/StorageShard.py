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

"""Module with the :class:`StorageShard` model class."""

from __future__ import annotations

import logging
import os
from typing import Any, override
from uuid import uuid4

from django.core.files.storage import default_storage
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin

from core.mixins.TimestampModelMixin import TimestampModelMixin
from eonvelope.utils.workarounds import get_config

logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class StorageShard(
    ExportModelOperationsMixin("storage_shard"), TimestampModelMixin, models.Model
):
    """A database model to keep track of and manage the sharded storage's status and structure.

    Important:
        Use the custom methods to create new instances, never use :func:`create`!
    """

    shard_directory_name = models.UUIDField(
        default=uuid4,
        editable=False,
        unique=True,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("shard directory name"),
    )
    """The name of the directory tracked by this entry. Unique."""

    file_count = models.PositiveSmallIntegerField(
        default=0,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("file count"),
    )
    """The number of files in this directory. 0 by default.
    Managed to not exceed :attr:`constance.get_config('STORAGE_MAX_FILES_PER_DIR')`."""

    current = models.BooleanField(
        default=False,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("status"),
    )
    """Flags whether this directory is the one where new data is being stored. False by default.
    There must only be one entry where this is set to True."""

    class Meta:
        """Metadata class for the model."""

        db_table = "storage_shards"
        """The name of the database table for the storage status."""
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name = _("storage shard")
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name_plural = _("storage shards")

    @override
    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the storage directory, using :attr:`path` and the state of the directory.
        """
        state = _("Current") if self.current else _("Archived")
        return _("%(state)s storage directory %(name)s") % {
            "state": state,
            "name": str(self.shard_directory_name),
        }

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Extended :django::func:`django.models.Model.save` method.

        Safely creates the new directory tracked by the instance in the storage.
        """
        if not self.pk:
            while True:
                path = default_storage.path(str(self.shard_directory_name))
                try:
                    os.makedirs(path, exist_ok=True)
                except FileExistsError:
                    self.shard_directory_name = uuid4()
                else:
                    break
        super().save(*args, **kwargs)

    def increment_file_count(self) -> None:
        """Increments the :attr:`file_count` within the limits of :attr:`constance.get_config('STORAGE_MAX_FILES_PER_DIR')`.

        If the result exceeds this limit, creates a new storage directory via :func:`_add_shard`.
        """
        logger.debug("Incrementing subdirectory count of %s ..", self)

        self.file_count += 1
        if self.file_count >= get_config("STORAGE_MAX_FILES_PER_DIR"):
            logger.debug(
                "Max number of subdirectories in %s reached, adding new storage ...",
                self,
            )
            self.current = False
            self.save(update_fields=["current", "file_count"])
            self._add_shard()
            logger.debug("Successfully added new storage.")
        else:
            self.save(update_fields=["file_count"])
        logger.debug("Successfully incremented subdirectory count.")

    def decrement_file_count(self) -> None:
        """Decrements the :attr:`file_count` but never below 0."""
        logger.debug("Decrementing subdirectory count of %s ..", self)
        if self.file_count > 0:
            self.file_count -= 1
            self.save(update_fields=["file_count"])
        logger.debug("Successfully decremented subdirectory count.")

    @classmethod
    def get_current_storage(cls) -> StorageShard:
        """Gets the current storage instance.

        Creates one if none is found.

        Returns:
            StorageShard: The currently used storage directory shard.
        """
        storage_entry = cls.objects.filter(current=True).first()
        if storage_entry is None:
            logger.info("Creating first storage directory...")
            storage_entry = cls._add_shard()
            logger.info("Successfully created first storage directory.")
        return storage_entry

    @classmethod
    def _add_shard(cls) -> StorageShard:
        """Adds a new current storage directory."""
        new_shard = cls(current=True)
        new_shard.save()
        return new_shard

    @classmethod
    def healthcheck(cls) -> bool:
        """Provides a healthcheck for the storage.

        Returns:
            True if storage is healthy,
            False if there is no unique current storage directory
            or the count of files for one of the directories is wrong.
        """
        unique_current = cls.objects.filter(current=True).count() in (0, 1)
        if not unique_current:
            logger.critical("More than one currently used storage directory!!!")
            return False

        root_listdir = default_storage.listdir("")
        correct_dir_count = cls.objects.count() == len(root_listdir[0])
        if not correct_dir_count:
            logger.critical(
                "Number of paths in storage doesn't match the index in the database!!!"
            )
            return False

        no_files_in_root = len(root_listdir[1]) == 0
        if not no_files_in_root:
            logger.critical("There are files in the storage root!!!")
            return False

        return True
