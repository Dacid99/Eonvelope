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

import time
from uuid import UUID

from celery import shared_task

from .models.Daemon import Daemon
from .utils.fetchers.exceptions import FetcherError


@shared_task
def fetch_emails(daemon_uuid_string: str) -> None:
    """Celery task to fetch and store emails.

    Args:
        daemon_uuid_string: The uuid of the daemon instance that manages this task.
    """
    try:
        daemon = Daemon.objects.select_related("mailbox", "mailbox__account").get(
            uuid=UUID(daemon_uuid_string)
        )
    except Daemon.DoesNotExist:
        return
    daemon.logger.info(
        "-------------------------------------------\nFetching emails ..."
    )
    start_time = time.time()
    try:
        daemon.mailbox.fetch(daemon.fetching_criterion)
    except FetcherError:
        daemon.logger.exception(
            "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nFailed to fetch emails!\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",
        )
        daemon.is_healthy = False
    else:
        daemon.is_healthy = True
    daemon.save(update_fields=["is_healthy"])

    end_time = time.time()
    daemon.logger.info(
        "Success fetching emails, completed in %s seconds\n!------------------------------------------",
        end_time - start_time,
    )
