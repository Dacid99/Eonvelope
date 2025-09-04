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

"""Save signal receivers for the :class:`core.models.Attachment` model."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from Emailkasten.models import UserProfile


if TYPE_CHECKING:
    from django.contrib.auth.models import User


logger = logging.getLogger(__name__)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def post_create_user(
    sender: User, instance: User, created: bool, **kwargs: Any
) -> None:
    """Receiver function deleting the file of the attachment from storage.

    Args:
        sender: The class type that sent the post_save signal.
        instance: The instance that has been saved.
        created: Whether the instance has just been created.
        **kwargs: Other keyword arguments.
    """
    if created:
        logger.debug("Creating profile for new user %s ...", instance)
        UserProfile.objects.create(user=instance)
        logger.debug("Successfully created new user profile.")
