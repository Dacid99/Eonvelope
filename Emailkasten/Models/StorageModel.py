# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import os

from django.db import models

from .. import constants

logger = logging.getLogger(__name__)
"""The logger instance for this module."""

class StorageModel(models.Model):
    """A database model to keep track of and manage the storage status and structure."""

    directory_number = models.PositiveIntegerField(unique=True)
    """The number of the directory tracked by this entry. Unique."""

    path = models.FilePathField(unique=True, path=constants.StorageConfiguration.STORAGE_PATH)
    """The path of the tracked directory. Unique.
    Must contain :attr:`Emailkasten.constants.StorageConfiguration.STORAGE_PATH`."""

    subdirectory_count = models.PositiveSmallIntegerField(default=0)
    """The number of subdirectories in this directory. 0 by default.
    Managed to not exceed :attr:`Emailkasten.constants.StorageConfiguration.MAX_SUBDIRS_PER_DIR`."""

    current = models.BooleanField(default=False)
    """Flags whether this directory is the one where new data is being stored. False by default.
    There must only be one entry where this is set to True."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""


    def __str__(self):
        state = "Current" if self.current else "Archived"
        return f"{state} storage directory {self.path}"


    def save(self, *args, **kwargs) -> None:
        """Extended :django::func:`django.models.Model.save` method with additional check for unique current directory and storage directory creation for new entries."""

        if StorageModel.objects.filter(current=True).count() > 1:
            logger.critical("More than one current storage directory!!")
        if not self.path:
            self.path = os.path.join(constants.StorageConfiguration.STORAGE_PATH, str(self.directory_number))
            if not os.path.exists( self.path ):
                logger.debug("Creating new storage directory %s ...", self.path)
                os.makedirs( self.path )
                logger.debug("Successfully created new storage directory.")

        super().save(*args, **kwargs)


    def incrementSubdirectoryCount(self) -> None:
        """Increments the :attr:`subdirectory_count` within the limits of :attr:`Emailkasten.constants.StorageConfiguration.MAX_SUBDIRS_PER_DIR`.
        If the result exceeds this limit, creates a new storage directory via :func:`_addNewDirectory`.
        """
        self.subdirectory_count += 1
        if self.subdirectory_count >= constants.StorageConfiguration.MAX_SUBDIRS_PER_DIR:
            self._addNewDirectory()
        else:
            self.save()


    def _addNewDirectory(self) -> None:
        """Adds a new storage directory by setting this entries :attr:`current` to `False` and creating a new database entry with incremented :attr:`directory_number` and :attr:`current` set to `True`.
        """
        self.current = False
        self.save(update_fields=['current'])
        StorageModel.objects.create(directory_number=self.directory_number+1, current=True, subdirectory_count=0)


    class Meta:
        db_table = "storage"
        """The name of the database table for the storage status."""


    @staticmethod
    def getSubdirectory(subdirectoryName: str) -> str:
        """Static utility to acquire a path for a subdirectory in the storage.
        If that subdirectory does not exist yet, creates it and increments the :attr:`subdirectory_count` of the current storage directory.

        Args:
            subdirectoryName: The name of subdirectory to be stored.

        Returns:
            str: The path of the subdirectory in the storage.
        """
        storageEntry = StorageModel.objects.filter(current=True).first()
        if not storageEntry:
            if os.listdir(constants.StorageConfiguration.STORAGE_PATH) and not StorageModel.objects.count():
                logger.critical("The storage is not empty but there is no information about it in the database!!")

            logger.info("The storage is empty, creating first storage directory.")
            storageEntry = StorageModel.objects.create(directory_number=0, current=True, subdirectory_count=0)
            logger.info("Successfully created first storage directory.")


        subdirectoryPath = os.path.join(storageEntry.path, subdirectoryName)
        if not os.path.exists(subdirectoryPath):
            logger.debug("Creating new subdirectory in the current storage directory ...")
            os.makedirs(subdirectoryPath)
            storageEntry.incrementSubdirectoryCount()
            logger.debug("Successfully created new subdirectory in the current storage directory.")


        return subdirectoryPath
