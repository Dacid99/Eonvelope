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

"""Delete signal receivers for the :class:`core.models.MailboxModel.MailboxModel` model."""
from __future__ import annotations

import logging
from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models.MailboxModel import MailboxModel


logger = logging.getLogger(__name__)
"""The logger instance for this module."""


@receiver(post_save, sender=MailboxModel)
def post_save_is_healthy(
    sender: MailboxModel, instance: MailboxModel, created: bool, **kwargs: Any
) -> None:
    """Receiver function flagging account and daemons of a mailbox according to a healthflag change.

    Once that mailbox becomes healthy again flags the account of that mailbox as healthy
    If a mailbox becomed unhealthy flags its daemons as unhealthy as well.

    Args:
        sender: The class type that sent the post_save signal.
        instance: The instance that has been saved.
        created: Whether the instance was newly created.
        **kwargs: Other keyword arguments

    Note:
        Using the batch `update` for the daemons does not trigger their post_save!
    """
    if created:
        return

    if instance.is_healthy:
        if "is_healthy" in instance.get_dirty_fields():
            logger.debug(
                "%s has become healthy, flagging its account as healthy ...",
                str(instance),
            )
            instance.account.is_healthy = True
            instance.account.save(update_fields=["is_healthy"])
            logger.debug("Successfully flagged account as healthy.")
    elif "is_healthy" in instance.get_dirty_fields():
        logger.debug(
            "%s has become unhealthy, flagging its daemons as unhealthy ...",
            str(instance),
        )
        instance.daemons.update(is_healthy=False)
        logger.debug("Successfully flagged account as healthy.")
