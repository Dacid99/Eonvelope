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

"""Module with the tasks for celery."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from celery import shared_task

from core.utils import FetchingCriterion
from core.utils.fetchers.exceptions import MailAccountError, MailboxError
from eonvelope.utils.workarounds import get_config

from .models.Daemon import Daemon
from .models.Email import Email
from .models.Mailbox import Mailbox


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
        daemon.mailbox.fetch(
            FetchingCriterion(daemon.fetching_criterion, daemon.fetching_criterion_arg)
        )
    except Exception as exc:
        daemon.set_unhealthy(exc)
        if isinstance(exc, MailAccountError):
            daemon.mailbox.account.set_unhealthy(exc)
        elif isinstance(exc, MailboxError):
            daemon.mailbox.set_unhealthy(exc)
        raise
    daemon.set_healthy()


@shared_task
def fetch_mailbox_emails(
    mailbox_id: int, fetching_criterion: str, fetching_criterion_arg: str = ""
) -> None:
    """Celery task to fetch and store emails.

    Args:
        mailbox_id: The id of the mailbox instance to fetch.
        fetching_criterion: The criterion to fetch on.
        fetching_criterion_arg: The argument for the criterion.
    """
    try:
        mailbox = Mailbox.objects.get(id=mailbox_id)
    except Mailbox.DoesNotExist:
        return
    try:
        mailbox.fetch(FetchingCriterion(fetching_criterion, fetching_criterion_arg))
    except Exception as exc:
        mailbox.set_unhealthy(exc)
        if isinstance(exc, MailAccountError):
            mailbox.account.set_unhealthy(exc)
        elif isinstance(exc, MailboxError):
            mailbox.set_unhealthy(exc)
        raise
    mailbox.set_healthy()


@shared_task
def process_emails_file(file_path: str, file_format: str, mailbox_id: int) -> None:
    """Celery task to process uploaded emails.

    Args:
        file_path: The path to the file to process.
        file_format: The format of the file.
        mailbox_id: The id of the mailbox to add the emails to.

    Raises:
        Exception: Any exception that is raised during fetching.
    """
    try:
        mailbox = Mailbox.objects.get(id=mailbox_id)
    except Mailbox.DoesNotExist:
        return
    with open(file_path, "br") as file:
        mailbox.add_emails_from_file(file, file_format)


@shared_task
def autodelete_expired_emails() -> None:
    """Celery task that removes emails older than their expiration date."""
    expiration_days = get_config("EMAIL_EXPIRATION_DAYS")
    if expiration_days <= 0:
        return
    deadline = datetime.now(tz=UTC) - timedelta(days=expiration_days)
    for email in Email.objects.filter(datetime__lt=deadline):
        email.delete()
