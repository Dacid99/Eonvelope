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

"""Delete signal receivers for the :class:`Emailkasten.Models.ImageModel.ImageModel` model."""

import logging
import os

from django.db.models.signals import post_delete
from django.dispatch import receiver

from ..Models.ImageModel import ImageModel


logger = logging.getLogger(__name__)


@receiver(post_delete, sender=ImageModel)
def post_delete_image(sender: ImageModel, instance: ImageModel, **kwargs) -> None:
    """Receiver function removing an image from the storage when its db entry is deleted.

    Args:
        sender: The class type that sent the post_delete signal.
        instance: The instance that has been deleted.
        **kwargs: Other keyword arguments.
    """
    if instance.file_path:
        logger.debug("Removing %s from storage ...", str(instance))
        try:
            os.remove(instance.file_path)
            logger.debug("Successfully removed the image file from storage.", exc_info=True)
        except FileNotFoundError:
            logger.error("%s was not found!", instance.file_path, exc_info=True)
        except OSError:
            logger.error("An OS error occured removing %s!", instance.file_path, exc_info=True)
        except Exception:
            logger.error("An unexpected error occured removing %s!", instance.file_path, exc_info=True)
