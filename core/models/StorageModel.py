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

"""Module with the :class:`StorageModel` model class."""

import logging
import os

from django.db import models

from Emailkasten.utils import get_config

logger = logging.getLogger(__name__)
"""The logger instance for this module."""

class StorageModel(models.Model):
    """A database model to keep track of and manage the sharded storage's status and structure.

    Important:
        Use the custom methods to create new instances, never use :func:`create`!"""

    directory_number = models.PositiveIntegerField(unique=True)
    """The number of the directory tracked by this entry. Unique."""

    path = models.FilePathField(unique=True, path=get_config('STORAGE_PATH'))
    """The path of the tracked directory. Unique.
    Must contain :attr:`constance.get_config('STORAGE_PATH')`."""

    subdirectory_count = models.PositiveSmallIntegerField(default=0)
    """The number of subdirectories in this directory. 0 by default.
    Managed to not exceed :attr:`constance.get_config('STORAGE_MAX_SUBDIRS_PER_DIR')`."""

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

    class Meta:
        """Metadata class for the model."""

        db_table = "storage"
        """The name of the database table for the storage status."""


    def save(self, *args, **kwargs) -> None:
        """Extended :django::func:`django.models.Model.save` method with additional check for unique current directory and storage directory creation for new entries."""

        if StorageModel.objects.filter(current=True).count() > 1:
            logger.critical("More than one current storage directory!!!")
        if not self.path:
            self.path = os.path.join(get_config('STORAGE_PATH'), str(self.directory_number))
            if not os.path.exists( self.path ):
                logger.info("Creating new storage directory %s ...", self.path)
                os.makedirs( self.path )
                logger.info("Successfully created new storage directory.")

        super().save(*args, **kwargs)


    def incrementSubdirectoryCount(self) -> None:
        """Increments the :attr:`subdirectory_count` within the limits of :attr:`constance.get_config('STORAGE_MAX_SUBDIRS_PER_DIR')`.
        If the result exceeds this limit, creates a new storage directory via :func:`_addNewDirectory`.
        """
        logger.debug("Incrementing subdirectory count of %s ..", str(self))

        self.subdirectory_count += 1
        self.save(update_fields=['subdirectory_count'])
        if self.subdirectory_count >= get_config('STORAGE_MAX_SUBDIRS_PER_DIR'):
            logger.debug("Max number of subdirectories in %s reached, adding new storage ...", str(self))
            self._addNewDirectory()
            logger.debug("Successfully added new storage.")

        logger.debug("Successfully incrementing subdirectory count.")


    def _addNewDirectory(self) -> None:
        """Adds a new storage directory by setting this entries :attr:`current` to `False`
        and creating a new database entry with incremented :attr:`directory_number` and :attr:`current` set to `True`.
        """
        self.current = False
        self.save(update_fields=['current'])
        StorageModel.objects.create(directory_number=self.directory_number+1, current=True, subdirectory_count=0)


    @staticmethod
    def getSubdirectory(subdirectoryName: str) -> str:
        """Static utility to acquire a path for a subdirectory in the storage.
        If that subdirectory does not exist yet, creates it and increments the :attr:`subdirectory_count` of the current storage directory.

        Args:
            subdirectoryName: The name of the subdirectory to be stored.

        Returns:
            The path of the subdirectory in the storage.
        """
        storageEntry = StorageModel.objects.filter(current=True).first()
        if not storageEntry:
            if os.listdir(get_config('STORAGE_PATH')) and not StorageModel.objects.count():
                logger.critical("The storage is not empty but there is no information about it in the database!!!")

            logger.info("Creating first storage directory...")
            storageEntry = StorageModel.objects.create(directory_number=0, current=True, subdirectory_count=0)
            logger.info("Successfully created first storage directory.")


        subdirectoryPath = os.path.join(storageEntry.path, subdirectoryName)
        if not os.path.exists(subdirectoryPath):
            logger.debug("Creating new subdirectory in the current storage directory ...")
            os.makedirs(subdirectoryPath)
            storageEntry.incrementSubdirectoryCount()
            logger.debug("Successfully created new subdirectory in the current storage directory.")

        return subdirectoryPath


    @staticmethod
    def healthcheck() -> bool:
        """Provides a healthcheck for the storage.

        Returns:
            True if storage is healthy,
            False if there is no unique current storage directory
            or the count of subdirectories for one of the directories is wrong.
        """
        uniqueCurrent = StorageModel.objects.filter(current=True).count() == 1
        if not uniqueCurrent:
            logger.critical("More than one currently used storage direcory!!!")

        correctSubdirCount = all(
            storage.subdirectory_count == len(os.listdir(storage.path)) for storage in StorageModel.objects.all()
        )
        if not correctSubdirCount:
            logger.critical("More subdirectories in a storage directory than indexed in database!!!")

        return uniqueCurrent and correctSubdirCount
