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

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest
from django.core.management import call_command
from freezegun import freeze_time
from model_bakery import baker

from core.models.AccountModel import AccountModel
from core.models.AttachmentModel import AttachmentModel
from core.models.CorrespondentModel import CorrespondentModel
from core.models.DaemonModel import DaemonModel
from core.models.EMailCorrespondentsModel import EMailCorrespondentsModel
from core.models.EMailModel import EMailModel
from core.models.MailboxModel import MailboxModel
from core.models.MailingListModel import MailingListModel


if TYPE_CHECKING:
    from django.db.models.query import QuerySet


def datetime_quarter(datetimeObject: datetime.datetime) -> int:
    """Calculate the quarter of the year for a given datetime.

    Args:
        datetimeObject: The datetime to calculate the quarter of.

    Returns:
        An `int` from 1-4 indicating the datetimes quarter of the year.
    """
    return (datetimeObject.month - 1) // 3 + 1


INT_TEST_ITEMS = [0, 1, 2]
LESSER_INT = -5
GREATER_INT = 6
DISJOINT_INT_RANGE = [7, 10]

INT_TEST_PARAMETERS = [
    ("__lte", INT_TEST_ITEMS[1], [0, 1]),
    ("__gte", INT_TEST_ITEMS[1], [1, 2]),
    ("__lt", INT_TEST_ITEMS[2], [0, 1]),
    ("__gt", INT_TEST_ITEMS[0], [1, 2]),
    ("", INT_TEST_ITEMS[1], [1]),
    ("__in", INT_TEST_ITEMS[0:2], [0, 1]),
    ("__range", INT_TEST_ITEMS[0:2], [0, 1]),
    ("__lte", LESSER_INT, []),
    ("__gte", GREATER_INT, []),
    ("__lt", LESSER_INT, []),
    ("__gt", GREATER_INT, []),
    ("", GREATER_INT, []),
    ("__in", DISJOINT_INT_RANGE, []),
    ("__range", DISJOINT_INT_RANGE, []),
]

FLOAT_TEST_ITEMS = [0.5, 1, 2.3]
LESSER_FLOAT = -5.4
GREATER_FLOAT = 6.1
DISJOINT_FLOAT_RANGE = [7.3, 10.2]

FLOAT_TEST_PARAMETERS = [
    ("__lte", FLOAT_TEST_ITEMS[1], [0, 1]),
    ("__gte", FLOAT_TEST_ITEMS[1], [1, 2]),
    ("__range", FLOAT_TEST_ITEMS[0:2], [0, 1]),
    ("__lte", LESSER_FLOAT, []),
    ("__gte", GREATER_FLOAT, []),
    ("__range", DISJOINT_FLOAT_RANGE, []),
]

BOOL_TEST_ITEMS = [True, False, False]

BOOL_TEST_PARAMETERS = [("", BOOL_TEST_ITEMS[0], [0]), ("", BOOL_TEST_ITEMS[1], [1, 2])]

TEXT_TEST_ITEMS = ["A1bCD", "ZyX9D", "ZbC8W"]

TEXT_TEST_PARAMETERS = [
    ("__icontains", TEXT_TEST_ITEMS[0][2:4].lower(), [0, 2]),
    ("__contains", TEXT_TEST_ITEMS[0][2:4], [0, 2]),
    ("", TEXT_TEST_ITEMS[1], [1]),
    ("__iexact", TEXT_TEST_ITEMS[1].lower(), [1]),
    ("__startswith", TEXT_TEST_ITEMS[1][0], [1, 2]),
    ("__istartswith", TEXT_TEST_ITEMS[1][0].lower(), [1, 2]),
    ("__endswith", TEXT_TEST_ITEMS[1][-1], [0, 1]),
    ("__iendswith", TEXT_TEST_ITEMS[1][-1].lower(), [0, 1]),
    ("__regex", r"\w{3}\d\w", [1, 2]),
    ("__iregex", r"\w{3}\d\w", [1, 2]),
    ("__in", TEXT_TEST_ITEMS[0:2], [0, 1]),
    ("__icontains", "op", []),
    ("__contains", "oP", []),
    ("", "No5PQ", []),
    ("__iexact", "no5pq", []),
    ("__startswith", "N", []),
    ("__istartswith", "n", []),
    ("__endswith", "Q", []),
    ("__iendswith", "q", []),
    ("__regex", r"\w{2}\d\w{2}", []),
    ("__iregex", r"\w{2}\d\w{2}", []),
    ("__in", ["No5PQ"], []),
]

DATETIME_TEST_ITEMS = [
    datetime.datetime(2001, 3, 7, 10, 20, 20),
    datetime.datetime(2002, 6, 13, 11, 30, 30),
    datetime.datetime(2003, 8, 15, 12, 40, 40),
]
LESSER_DATETIME = datetime.datetime(1990, 2, 5, 5, 10, 10)
GREATER_DATETIME = datetime.datetime(2020, 10, 24, 20, 50, 50)
DISJOINT_DATETIME_RANGE = [
    datetime.datetime(2020, 10, 24, 20, 50, 50),
    datetime.datetime(2021, 11, 28, 21, 55, 55),
]

DATETIME_TEST_PARAMETERS = [
    ("__date", DATETIME_TEST_ITEMS[1], [1]),
    ("__date__gte", DATETIME_TEST_ITEMS[1], [1, 2]),
    ("__date__lte", DATETIME_TEST_ITEMS[1], [0, 1]),
    ("__date__gt", DATETIME_TEST_ITEMS[0], [1, 2]),
    ("__date__lt", DATETIME_TEST_ITEMS[2], [0, 1]),
    ("__date__in", DATETIME_TEST_ITEMS[0:2], [0, 1]),
    ("__date__range", DATETIME_TEST_ITEMS[1:3], [1, 2]),
    ("__time", DATETIME_TEST_ITEMS[1].time(), [1]),
    ("__time__gte", DATETIME_TEST_ITEMS[1].time(), [1, 2]),
    ("__time__lte", DATETIME_TEST_ITEMS[1].time(), [0, 1]),
    ("__time__gt", DATETIME_TEST_ITEMS[0].time(), [1, 2]),
    ("__time__lt", DATETIME_TEST_ITEMS[2].time(), [0, 1]),
    ("__time__in", [item.time() for item in DATETIME_TEST_ITEMS[0:2]], [0, 1]),
    ("__time__range", [item.time() for item in DATETIME_TEST_ITEMS[1:3]], [1, 2]),
    ("__iso_year", DATETIME_TEST_ITEMS[2].isocalendar().year, [2]),
    ("__iso_year__gte", DATETIME_TEST_ITEMS[1].isocalendar().year, [1, 2]),
    ("__iso_year__lte", DATETIME_TEST_ITEMS[1].isocalendar().year, [0, 1]),
    ("__iso_year__gt", DATETIME_TEST_ITEMS[0].isocalendar().year, [1, 2]),
    ("__iso_year__lt", DATETIME_TEST_ITEMS[2].isocalendar().year, [0, 1]),
    (
        "__iso_year__in",
        [item.isocalendar().year for item in DATETIME_TEST_ITEMS[0:2]],
        [0, 1],
    ),
    (
        "__iso_year__range",
        [item.isocalendar().year for item in DATETIME_TEST_ITEMS[1:3]],
        [1, 2],
    ),
    ("__month", DATETIME_TEST_ITEMS[1].month, [1]),
    ("__month__gte", DATETIME_TEST_ITEMS[1].month, [1, 2]),
    ("__month__lte", DATETIME_TEST_ITEMS[1].month, [0, 1]),
    ("__month__gt", DATETIME_TEST_ITEMS[0].month, [1, 2]),
    ("__month__lt", DATETIME_TEST_ITEMS[2].month, [0, 1]),
    ("__month__in", [item.month for item in DATETIME_TEST_ITEMS[0:2]], [0, 1]),
    ("__month__range", [item.month for item in DATETIME_TEST_ITEMS[1:3]], [1, 2]),
    ("__quarter", datetime_quarter(DATETIME_TEST_ITEMS[1]), [1]),
    ("__quarter__gte", datetime_quarter(DATETIME_TEST_ITEMS[1]), [1, 2]),
    ("__quarter__lte", datetime_quarter(DATETIME_TEST_ITEMS[1]), [0, 1]),
    ("__quarter__gt", datetime_quarter(DATETIME_TEST_ITEMS[0]), [1, 2]),
    ("__quarter__lt", datetime_quarter(DATETIME_TEST_ITEMS[2]), [0, 1]),
    (
        "__quarter__in",
        [datetime_quarter(item) for item in DATETIME_TEST_ITEMS[0:2]],
        [0, 1],
    ),
    (
        "__quarter__range",
        [datetime_quarter(item) for item in DATETIME_TEST_ITEMS[1:3]],
        [1, 2],
    ),
    ("__week", DATETIME_TEST_ITEMS[1].isocalendar().week, [1]),
    ("__week__gte", DATETIME_TEST_ITEMS[1].isocalendar().week, [1, 2]),
    ("__week__lte", DATETIME_TEST_ITEMS[1].isocalendar().week, [0, 1]),
    ("__week__gt", DATETIME_TEST_ITEMS[0].isocalendar().week, [1, 2]),
    ("__week__lt", DATETIME_TEST_ITEMS[2].isocalendar().week, [0, 1]),
    (
        "__week__in",
        [item.isocalendar().week for item in DATETIME_TEST_ITEMS[0:2]],
        [0, 1],
    ),
    (
        "__week__range",
        [item.isocalendar().week for item in DATETIME_TEST_ITEMS[1:3]],
        [1, 2],
    ),
    ("__iso_week_day", DATETIME_TEST_ITEMS[1].isoweekday(), [1]),
    ("__iso_week_day__gte", DATETIME_TEST_ITEMS[1].isoweekday(), [1, 2]),
    ("__iso_week_day__lte", DATETIME_TEST_ITEMS[1].isoweekday(), [0, 1]),
    ("__iso_week_day__gt", DATETIME_TEST_ITEMS[0].isoweekday(), [1, 2]),
    ("__iso_week_day__lt", DATETIME_TEST_ITEMS[2].isoweekday(), [0, 1]),
    (
        "__iso_week_day__in",
        [item.isoweekday() for item in DATETIME_TEST_ITEMS[0:2]],
        [0, 1],
    ),
    (
        "__iso_week_day__range",
        [item.isoweekday() for item in DATETIME_TEST_ITEMS[1:3]],
        [1, 2],
    ),
    ("__day", DATETIME_TEST_ITEMS[1].day, [1]),
    ("__day__gte", DATETIME_TEST_ITEMS[1].day, [1, 2]),
    ("__day__lte", DATETIME_TEST_ITEMS[1].day, [0, 1]),
    ("__day__gt", DATETIME_TEST_ITEMS[0].day, [1, 2]),
    ("__day__lt", DATETIME_TEST_ITEMS[2].day, [0, 1]),
    ("__day__in", [item.day for item in DATETIME_TEST_ITEMS[0:2]], [0, 1]),
    ("__day__range", [item.day for item in DATETIME_TEST_ITEMS[1:3]], [1, 2]),
    ("__hour", DATETIME_TEST_ITEMS[1].hour, [1]),
    ("__hour__gte", DATETIME_TEST_ITEMS[1].hour, [1, 2]),
    ("__hour__lte", DATETIME_TEST_ITEMS[1].hour, [0, 1]),
    ("__hour__gt", DATETIME_TEST_ITEMS[0].hour, [1, 2]),
    ("__hour__lt", DATETIME_TEST_ITEMS[2].hour, [0, 1]),
    ("__hour__in", [item.hour for item in DATETIME_TEST_ITEMS[0:2]], [0, 1]),
    ("__hour__range", [item.hour for item in DATETIME_TEST_ITEMS[1:3]], [1, 2]),
    ("__minute", DATETIME_TEST_ITEMS[1].minute, [1]),
    ("__minute__gte", DATETIME_TEST_ITEMS[1].minute, [1, 2]),
    ("__minute__lte", DATETIME_TEST_ITEMS[1].minute, [0, 1]),
    ("__minute__gt", DATETIME_TEST_ITEMS[0].minute, [1, 2]),
    ("__minute__lt", DATETIME_TEST_ITEMS[2].minute, [0, 1]),
    ("__minute__in", [item.minute for item in DATETIME_TEST_ITEMS[0:2]], [0, 1]),
    ("__minute__range", [item.minute for item in DATETIME_TEST_ITEMS[1:3]], [1, 2]),
    ("__second", DATETIME_TEST_ITEMS[1].second, [1]),
    ("__second__gte", DATETIME_TEST_ITEMS[1].second, [1, 2]),
    ("__second__lte", DATETIME_TEST_ITEMS[1].second, [0, 1]),
    ("__second__gt", DATETIME_TEST_ITEMS[0].second, [1, 2]),
    ("__second__lt", DATETIME_TEST_ITEMS[2].second, [0, 1]),
    ("__second__in", [item.second for item in DATETIME_TEST_ITEMS[0:2]], [0, 1]),
    ("__second__range", [item.second for item in DATETIME_TEST_ITEMS[1:3]], [1, 2]),
    ("__date", GREATER_DATETIME, []),
    ("__date__gte", GREATER_DATETIME, []),
    ("__date__lte", LESSER_DATETIME, []),
    ("__date__gt", GREATER_DATETIME, []),
    ("__date__lt", LESSER_DATETIME, []),
    ("__date__in", DISJOINT_DATETIME_RANGE, []),
    ("__date__range", DISJOINT_DATETIME_RANGE, []),
    ("__time", GREATER_DATETIME.time(), []),
    ("__time__gte", GREATER_DATETIME.time(), []),
    ("__time__lte", LESSER_DATETIME.time(), []),
    ("__time__gt", GREATER_DATETIME.time(), []),
    ("__time__lt", LESSER_DATETIME.time(), []),
    ("__time__in", [item.time() for item in DISJOINT_DATETIME_RANGE], []),
    ("__time__range", [item.time() for item in DISJOINT_DATETIME_RANGE], []),
    ("__iso_year", GREATER_DATETIME.isocalendar().year, []),
    ("__iso_year__gte", GREATER_DATETIME.isocalendar().year, []),
    ("__iso_year__lte", LESSER_DATETIME.isocalendar().year, []),
    ("__iso_year__gt", GREATER_DATETIME.isocalendar().year, []),
    ("__iso_year__lt", LESSER_DATETIME.isocalendar().year, []),
    (
        "__iso_year__in",
        [item.isocalendar().year for item in DISJOINT_DATETIME_RANGE],
        [],
    ),
    (
        "__iso_year__range",
        [item.isocalendar().year for item in DISJOINT_DATETIME_RANGE],
        [],
    ),
    ("__month", GREATER_DATETIME.month, []),
    ("__month__gte", GREATER_DATETIME.month, []),
    ("__month__lte", LESSER_DATETIME.month, []),
    ("__month__gt", GREATER_DATETIME.month, []),
    ("__month__lt", LESSER_DATETIME.month, []),
    ("__month__in", [item.month for item in DISJOINT_DATETIME_RANGE], []),
    ("__month__range", [item.month for item in DISJOINT_DATETIME_RANGE], []),
    ("__quarter", datetime_quarter(GREATER_DATETIME), []),
    ("__quarter__gte", datetime_quarter(GREATER_DATETIME), []),
    ("__quarter__lte", datetime_quarter(LESSER_DATETIME), [0]),
    ("__quarter__gt", datetime_quarter(GREATER_DATETIME), []),
    ("__quarter__lt", datetime_quarter(LESSER_DATETIME), []),
    ("__quarter__in", [datetime_quarter(item) for item in DISJOINT_DATETIME_RANGE], []),
    (
        "__quarter__range",
        [datetime_quarter(item) for item in DISJOINT_DATETIME_RANGE],
        [],
    ),
    ("__week", GREATER_DATETIME.isocalendar().week, []),
    ("__week__gte", GREATER_DATETIME.isocalendar().week, []),
    ("__week__lte", LESSER_DATETIME.isocalendar().week, []),
    ("__week__gt", GREATER_DATETIME.isocalendar().week, []),
    ("__week__lt", LESSER_DATETIME.isocalendar().week, []),
    ("__week__in", [item.isocalendar().week for item in DISJOINT_DATETIME_RANGE], []),
    (
        "__week__range",
        [item.isocalendar().week for item in DISJOINT_DATETIME_RANGE],
        [],
    ),
    ("__iso_week_day", GREATER_DATETIME.isoweekday(), []),
    ("__iso_week_day__gte", GREATER_DATETIME.isoweekday(), []),
    ("__iso_week_day__lte", LESSER_DATETIME.isoweekday(), []),
    ("__iso_week_day__gt", GREATER_DATETIME.isoweekday(), []),
    ("__iso_week_day__lt", LESSER_DATETIME.isoweekday(), []),
    ("__iso_week_day__in", [item.isoweekday() for item in DISJOINT_DATETIME_RANGE], []),
    (
        "__iso_week_day__range",
        [item.isoweekday() for item in DISJOINT_DATETIME_RANGE],
        [],
    ),
    ("__day", GREATER_DATETIME.day, []),
    ("__day__gte", GREATER_DATETIME.day, []),
    ("__day__lte", LESSER_DATETIME.day, []),
    ("__day__gt", GREATER_DATETIME.day, []),
    ("__day__lt", LESSER_DATETIME.day, []),
    ("__day__in", [item.day for item in DISJOINT_DATETIME_RANGE], []),
    ("__day__range", [item.day for item in DISJOINT_DATETIME_RANGE], []),
    ("__hour", GREATER_DATETIME.hour, []),
    ("__hour__gte", GREATER_DATETIME.hour, []),
    ("__hour__lte", LESSER_DATETIME.hour, []),
    ("__hour__gt", GREATER_DATETIME.hour, []),
    ("__hour__lt", LESSER_DATETIME.hour, []),
    ("__hour__in", [item.hour for item in DISJOINT_DATETIME_RANGE], []),
    ("__hour__range", [item.hour for item in DISJOINT_DATETIME_RANGE], []),
    ("__minute", GREATER_DATETIME.minute, []),
    ("__minute__gte", GREATER_DATETIME.minute, []),
    ("__minute__lte", LESSER_DATETIME.minute, []),
    ("__minute__gt", GREATER_DATETIME.minute, []),
    ("__minute__lt", LESSER_DATETIME.minute, []),
    ("__minute__in", [item.minute for item in DISJOINT_DATETIME_RANGE], []),
    ("__minute__range", [item.minute for item in DISJOINT_DATETIME_RANGE], []),
    ("__second", GREATER_DATETIME.second, []),
    ("__second__gte", GREATER_DATETIME.second, []),
    ("__second__lte", LESSER_DATETIME.second, []),
    ("__second__gt", GREATER_DATETIME.second, []),
    ("__second__lt", LESSER_DATETIME.second, []),
    ("__second__in", [item.second for item in DISJOINT_DATETIME_RANGE], []),
    ("__second__range", [item.second for item in DISJOINT_DATETIME_RANGE], []),
]


@pytest.fixture(scope="package")
def unblocked_db(django_db_setup, django_db_blocker):
    """Fixture safely unblocking the database for scoped db fixtures."""
    with django_db_blocker.unblock():
        yield
        call_command("flush", "--no-input")


@pytest.fixture(scope="package")
def account_queryset(unblocked_db) -> QuerySet[AccountModel, AccountModel]:
    """Fixture adding accounts with the test attributes to the database and returns them in a queryset."""
    for number, text_test_item in enumerate(TEXT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                AccountModel,
                mail_address=text_test_item,
                mail_host=text_test_item,
                mail_host_port=INT_TEST_ITEMS[number],
                timeout=FLOAT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                is_healthy=BOOL_TEST_ITEMS[number],
            )

    return AccountModel.objects.all()


@pytest.fixture(scope="package")
def mailbox_queryset(
    unblocked_db, account_queryset
) -> QuerySet[MailboxModel, MailboxModel]:
    """Fixture adding mailboxes with the test attributes to the database and returns them in a queryset."""
    for number, text_test_item in enumerate(TEXT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                MailboxModel,
                name=text_test_item,
                save_toEML=BOOL_TEST_ITEMS[number],
                save_attachments=BOOL_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                is_healthy=BOOL_TEST_ITEMS[number],
                account=account_queryset.get(id=number + 1),
            )

    return MailboxModel.objects.all()


@pytest.fixture(scope="package")
def daemon_queryset(
    unblocked_db, mailbox_queryset
) -> QuerySet[DaemonModel, DaemonModel]:
    """Fixture adding daemons with the test attributes to the database and returns them in a queryset."""
    for number, int_test_item in enumerate(INT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                DaemonModel,
                cycle_interval=int_test_item,
                is_running=BOOL_TEST_ITEMS[number],
                is_healthy=BOOL_TEST_ITEMS[number],
                mailbox=mailbox_queryset.get(id=number + 1),
                log_filepath=TEXT_TEST_ITEMS[number],
            )

    return DaemonModel.objects.all()


@pytest.fixture(scope="package")
def correspondent_queryset(
    unblocked_db,
) -> QuerySet[CorrespondentModel, CorrespondentModel]:
    """Fixture adding correspondents with the test attributes to the database and returns them in a queryset."""
    for number, text_test_item in enumerate(TEXT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                CorrespondentModel,
                email_name=text_test_item,
                email_address=text_test_item,
                is_favorite=BOOL_TEST_ITEMS[number],
            )

    return CorrespondentModel.objects.all()


@pytest.fixture(scope="package")
def mailinglist_queryset(unblocked_db) -> QuerySet[MailingListModel, MailingListModel]:
    """Fixture adding mailinglists with the test attributes to the database and returns them in a queryset."""
    for number, text_test_item in enumerate(TEXT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                MailingListModel,
                list_id=text_test_item,
                list_owner=text_test_item,
                list_subscribe=text_test_item,
                list_unsubscribe=text_test_item,
                list_post=text_test_item,
                list_help=text_test_item,
                list_archive=text_test_item,
                is_favorite=BOOL_TEST_ITEMS[number],
            )

    return MailingListModel.objects.all()


@pytest.fixture(scope="package")
def email_queryset(
    unblocked_db,
    mailbox_queryset,
    correspondent_queryset,
    mailinglist_queryset,
) -> QuerySet[EMailModel, EMailModel]:
    """Fixture adding emails with the test attributes to the database and returns them in a queryset."""
    for number, text_test_item in enumerate(TEXT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            new_email = baker.make(
                EMailModel,
                message_id=text_test_item,
                datetime=datetime.datetime.now(tz=datetime.UTC),
                email_subject=text_test_item,
                plain_bodytext=text_test_item,
                html_bodytext=text_test_item,
                datasize=INT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                mailbox=mailbox_queryset.get(id=number + 1),
                mailinglist=mailinglist_queryset.get(id=number + 1),
                x_spam=text_test_item,
            )
            baker.make(
                EMailCorrespondentsModel,
                email=new_email,
                correspondent=correspondent_queryset.get(id=number + 1),
            )

    return EMailModel.objects.all()


@pytest.fixture(scope="package")
def attachment_queryset(
    unblocked_db, email_queryset
) -> QuerySet[AttachmentModel, AttachmentModel]:
    """Fixture adding attachments with the test attributes to the database and returns them in a queryset."""
    for number, text_test_item in enumerate(TEXT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                AttachmentModel,
                file_path="/path/" + text_test_item,
                file_name=text_test_item,
                content_disposition=text_test_item,
                content_type=text_test_item,
                datasize=INT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                email=email_queryset.get(id=number + 1),
            )

    return AttachmentModel.objects.all()
