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

"""Save signal receivers for the :class:`core.models.Account` model."""

from __future__ import annotations

import logging
from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Account


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Account)
def post_save_account_is_healthy(
    sender: Account,
    instance: Account,
    created: bool,  # noqa: FBT001  # required for receiver decorator
    **kwargs: Any,
) -> None:
    """Receiver function flagging all mailboxes of an account as unhealthy once that account becomes unhealthy.

    Args:
        sender: The class type that sent the post_save signal.
        instance: The instance that has been saved.
        created: Whether the instance was newly created.
        **kwargs: Other keyword arguments.
    """
    if created or instance.is_healthy is None:
        return

    if not instance.is_healthy and "is_healthy" in instance.get_dirty_fields():
        logger.debug(
            "%s has become unhealthy, flagging all its mailboxes as unhealthy ...",
            instance,
        )
        mailbox_entries = instance.mailboxes.all()
        for mailbox_entry in mailbox_entries:
            mailbox_entry.set_unhealthy(instance.last_error)
        logger.debug("Successfully flagged mailboxes as unhealthy.")
