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

"""Save signal receivers for the :class:`core.models.Email` model."""

from __future__ import annotations

import logging
from typing import Any

from django.db.models.signals import post_delete
from django.dispatch import receiver

from core.models import Email


logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Email)
def post_delete_email(sender: Email, instance: Email, **kwargs: Any) -> None:
    """Receiver function deleting the .eml file of the email from storage.

    Args:
        sender: The class type that sent the post_save signal.
        instance: The instance that has been deleted.
        **kwargs: Other keyword arguments.
    """
    instance.delete_file()
