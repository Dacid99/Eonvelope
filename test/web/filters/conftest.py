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

"""File with fixtures and configurations required for web/filters tests. Automatically imported to test_ files."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest
from django.core.management import call_command
from django_celery_beat.models import IntervalSchedule
from freezegun import freeze_time
from model_bakery import baker

from core.constants import EmailFetchingCriterionChoices, EmailProtocolChoices
from core.models import (
    Account,
    Attachment,
    Correspondent,
    Daemon,
    Email,
    EmailCorrespondent,
    Mailbox,
)


if TYPE_CHECKING:
    from django.db.models import QuerySet


INT_TEST_ITEMS = [0, 1, 2]
LESSER_INT = -5
GREATER_INT = 6
DISJOINT_INT_RANGE = [7, 10]

INT_TEST_PARAMETERS = [
    ("__range", INT_TEST_ITEMS[0:2], [0, 1]),
    ("__range", DISJOINT_INT_RANGE, []),
]

FLOAT_TEST_ITEMS = [0.5, 1, 2.3]
LESSER_FLOAT = -5.4
GREATER_FLOAT = 6.1
DISJOINT_FLOAT_RANGE = [7.3, 10.2]

FLOAT_TEST_PARAMETERS = [
    ("__range", FLOAT_TEST_ITEMS[0:2], [0, 1]),
    ("__range", DISJOINT_FLOAT_RANGE, []),
]

BOOL_TEST_ITEMS = [True, False, False]

BOOL_TEST_PARAMETERS = [
    ("", BOOL_TEST_ITEMS[0], [0]),
    ("", BOOL_TEST_ITEMS[1], [1, 2]),
]

TEXT_TEST_ITEMS = ["A1bCD", "ZyX9D", "ZbC8W"]

TEXT_TEST_PARAMETERS = [
    ("__icontains", TEXT_TEST_ITEMS[0][2:4].lower(), [0, 2]),
    ("__icontains", "op", []),
    ("__icontains", None, [0, 1, 2]),
]

DATETIME_TEST_ITEMS = [
    datetime.datetime(2001, 3, 7, 10, 20, 20, tzinfo=datetime.UTC),
    datetime.datetime(2002, 6, 13, 11, 30, 30, tzinfo=datetime.UTC),
    datetime.datetime(2003, 8, 15, 12, 40, 4, tzinfo=datetime.UTC),
]
LESSER_DATETIME = datetime.datetime(1990, 2, 5, 5, 10, 10, tzinfo=datetime.UTC)
GREATER_DATETIME = datetime.datetime(2020, 10, 24, 20, 50, 50, tzinfo=datetime.UTC)
DISJOINT_DATETIME_RANGE = [
    datetime.datetime(2020, 10, 24, 20, 50, 50, tzinfo=datetime.UTC),
    datetime.datetime(2021, 11, 28, 21, 55, 55, tzinfo=datetime.UTC),
]

DATETIME_TEST_PARAMETERS = [
    ("__date__gte", DATETIME_TEST_ITEMS[1], [1, 2]),
    ("__date__lte", DATETIME_TEST_ITEMS[1], [0, 1]),
    ("__date__gte", GREATER_DATETIME, []),
    ("__date__lte", LESSER_DATETIME, []),
]

CHOICES_TEST_PARAMETERS = [
    ("", [0], [0]),
    ("", [0, 2], [0, 2]),
]


@pytest.fixture(scope="package")
def unblocked_db(django_db_setup, django_db_blocker):
    """Fixture safely unblocking the database for scoped db fixtures."""
    with django_db_blocker.unblock():
        yield
        call_command("flush", "--no-input")


@pytest.fixture(scope="package")
def account_queryset(unblocked_db) -> QuerySet[Account, Account]:
    """Fixture adding accounts with the test attributes to the database and returns them in a queryset."""
    for number, text_test_item in enumerate(TEXT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                Account,
                mail_address=text_test_item,
                mail_host=text_test_item,
                mail_host_port=INT_TEST_ITEMS[number],
                protocol=EmailProtocolChoices.values[number],
                timeout=FLOAT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                is_healthy=BOOL_TEST_ITEMS[number],
            )

    return Account.objects.all()


@pytest.fixture(scope="package")
def mailbox_queryset(unblocked_db, account_queryset) -> QuerySet[Mailbox, Mailbox]:
    """Fixture adding mailboxes with the test attributes to the database and returns them in a queryset."""
    for number, text_test_item in enumerate(TEXT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                Mailbox,
                name=text_test_item,
                save_to_eml=BOOL_TEST_ITEMS[number],
                save_attachments=BOOL_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                is_healthy=BOOL_TEST_ITEMS[number],
                account=account_queryset.get(id=number + 1),
            )

    return Mailbox.objects.all()


@pytest.fixture(scope="package")
def daemon_queryset(unblocked_db, mailbox_queryset) -> QuerySet[Daemon, Daemon]:
    """Fixture adding daemons with the test attributes to the database and returns them in a queryset."""
    for number, text_test_item in enumerate(TEXT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            interval = baker.make(
                IntervalSchedule,
                every=INT_TEST_ITEMS[number],
                period=IntervalSchedule.PERIOD_CHOICES[number][0],
            )
            baker.make(
                Daemon,
                fetching_criterion=EmailFetchingCriterionChoices.values[number],
                interval=interval,
                is_healthy=BOOL_TEST_ITEMS[number],
                mailbox=mailbox_queryset.get(id=number + 1),
                log_filepath=text_test_item,
            )

    return Daemon.objects.all()


@pytest.fixture(scope="package")
def correspondent_queryset(
    unblocked_db,
) -> QuerySet[Correspondent, Correspondent]:
    """Fixture adding correspondents with the test attributes to the database and returns them in a queryset."""
    for number, text_test_item in enumerate(TEXT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                Correspondent,
                list_id=text_test_item,
                list_owner=text_test_item,
                list_subscribe=text_test_item,
                list_unsubscribe=text_test_item,
                list_post=text_test_item,
                list_help=text_test_item,
                list_archive=text_test_item,
                email_name=text_test_item,
                email_address=text_test_item,
                is_favorite=BOOL_TEST_ITEMS[number],
            )

    return Correspondent.objects.all()


@pytest.fixture(scope="package")
def email_queryset(
    unblocked_db,
    mailbox_queryset,
) -> QuerySet[Email, Email]:
    """Fixture adding emails with the test attributes to the database and returns them in a queryset."""
    for number, text_test_item in enumerate(TEXT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                Email,
                message_id=text_test_item,
                datetime=datetime.datetime.now(tz=datetime.UTC),
                email_subject=text_test_item,
                plain_bodytext=text_test_item,
                html_bodytext=text_test_item,
                datasize=INT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                mailbox=mailbox_queryset.get(id=number + 1),
                x_spam=text_test_item,
            )

    return Email.objects.all()


@pytest.fixture(scope="package")
def emailcorrespondents_queryset(
    unblocked_db, email_queryset, correspondent_queryset
) -> QuerySet[EmailCorrespondent, EmailCorrespondent]:
    """Fixture adding correspondents with the test attributes to the database and returns them in a queryset."""
    for number, datetime_test_item in enumerate(DATETIME_TEST_ITEMS):
        with freeze_time(datetime_test_item):
            baker.make(
                EmailCorrespondent,
                email=email_queryset.get(id=number + 1),
                correspondent=correspondent_queryset.get(id=number + 1),
            )

    return EmailCorrespondent.objects.all()


@pytest.fixture(scope="package")
def attachment_queryset(
    unblocked_db, email_queryset
) -> QuerySet[Attachment, Attachment]:
    """Fixture adding attachments with the test attributes to the database and returns them in a queryset."""
    for number, text_test_item in enumerate(TEXT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                Attachment,
                file_path="/path/" + text_test_item,
                file_name=text_test_item,
                content_disposition=text_test_item,
                content_id=text_test_item,
                content_maintype=text_test_item,
                content_subtype=text_test_item,
                datasize=INT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                email=email_queryset.get(id=number + 1),
            )

    return Attachment.objects.all()
