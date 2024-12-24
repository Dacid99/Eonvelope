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

"""Delete signal receivers for the :class:`Emailkasten.Models.EMailModel.EMailModel` model."""

import logging
import os

from django.db.models.signals import post_delete
from django.dispatch import receiver

from ..Models.EMailModel import EMailModel


logger = logging.getLogger(__name__)


@receiver(post_delete, sender=EMailModel)
def post_delete_email_files(sender: EMailModel, instance:EMailModel, **kwargs) -> None:
    """Receiver function removing the files for an email from the storage when its db entry is deleted.

    Args:
        sender: The class type that sent the post_delete signal.
        instance: The instance that has been deleted.
        **kwargs: Other keyword arguments.
    """
    logger.debug("Removing files for %s from storage ...", str(instance))
    if instance.eml_filepath:
        try:
            os.remove(instance.eml_filepath)
            logger.debug("Successfully removed the emails .eml file from storage.", exc_info=True)
        except FileNotFoundError:
            logger.error("%s was not found!", instance.eml_filepath, exc_info=True)
        except PermissionError:
            logger.error("Permission to remove %s was denied!", instance.eml_filepath, exc_info=True)
        except IsADirectoryError:
            logger.error("%s is a directory, not a file!", instance.eml_filepath, exc_info=True)
        except OSError:
            logger.error("An OS error occured removing %s!", instance.eml_filepath, exc_info=True)
        except Exception:
            logger.error("An unexpected error occured removing %s!", instance.eml_filepath, exc_info=True)

    if instance.prerender_filepath:
        try:
            os.remove(instance.prerender_filepath)
            logger.debug("Successfully removed the emails .eml file from storage.", exc_info=True)
        except FileNotFoundError:
            logger.error("%s was not found!", instance.prerender_filepath, exc_info=True)
        except PermissionError:
            logger.error("Permission to remove %s was denied!", instance.prerender_filepath, exc_info=True)
        except IsADirectoryError:
            logger.error("%s is a directory, not a file!", instance.prerender_filepath, exc_info=True)
        except OSError:
            logger.error("An OS error occured removing %s!", instance.prerender_filepath, exc_info=True)
        except Exception:
            logger.error("An unexpected error occured removing %s!", instance.prerender_filepath, exc_info=True)
