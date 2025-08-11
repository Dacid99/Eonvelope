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

"""Module with the tasks for celery."""

from uuid import UUID

from celery import shared_task

from core.utils.fetchers.exceptions import MailAccountError, MailboxError

from .models.Daemon import Daemon


@shared_task
def fetch_emails(  # this must not be renamed or moved, otherwise existing daemons will break!
    daemon_uuid_string: str,
) -> None:
    """Celery task to fetch and store emails.

    Args:
        daemon_uuid_string: The uuid of the daemon instance that manages this task.

    Raises:
        Exception: Any exception that is raised during fetching.
    """
    try:
        daemon = Daemon.objects.select_related("mailbox").get(
            uuid=UUID(daemon_uuid_string)
        )
    except Daemon.DoesNotExist:
        return
    try:
        daemon.mailbox.fetch(daemon.fetching_criterion)
    except Exception as exc:
        daemon.is_healthy = False
        daemon.last_error = str(exc)
        daemon.save(update_fields=["is_healthy", "last_error"])
        if isinstance(exc, MailAccountError):
            daemon.mailbox.account.is_healthy = False
            daemon.mailbox.account.save(update_fields=["is_healthy"])
        elif isinstance(exc, MailboxError):
            daemon.mailbox.is_healthy = False
            daemon.mailbox.save(update_fields=["is_healthy"])
        raise
    else:
        daemon.is_healthy = True
        daemon.save(update_fields=["is_healthy"])
