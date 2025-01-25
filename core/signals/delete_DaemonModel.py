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

"""Delete signal receivers for the :class:`core.models.DaemonModel.DaemonModel` model."""

import logging

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from core.models.DaemonModel import DaemonModel
from core.EMailArchiverDaemonRegistry import EMailArchiverDaemonRegistry

logger = logging.getLogger(__name__)

@receiver(pre_delete, sender=DaemonModel)
def pre_delete_stop_daemon(sender: DaemonModel, instance: DaemonModel, **kwargs):
    """Receiver function stopping the daemon once its daemon database entry is deleted.

    Args:
        sender: The class type that sent the pre_delete signal.
        instance: The instance that has been saved.
        **kwargs: Other keyword arguments.
    """
    logger.debug("Stopping daemon of deleted daemon %s ..", str(instance))
    EMailArchiverDaemonRegistry.stopDaemon(instance)
    logger.debug("Successfully stopped daemon of deleted daemon %s.", str(instance))
