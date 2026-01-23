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

"""File with fixtures and configurations required for api/v1/filters tests. Automatically imported to `test_` files."""

from __future__ import annotations

import datetime

import pytest
from django.core.management import call_command
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from freezegun import freeze_time
from model_bakery import baker

from core.models import (
    Account,
    Attachment,
    Correspondent,
    Daemon,
    Email,
    EmailCorrespondent,
    Mailbox,
)


def datetime_quarter(datetime_object: datetime.datetime):
    """Calculate the quarter of the year for a given datetime.

    Args:
        datetime_object: A datetime.

    Returns:
        An `int` from 1-4 indicating the datetimes quarter of the year.
    """
    return (datetime_object.month - 1) // 3 + 1


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
]

FLOAT_TEST_ITEMS = [0.5, 1, 2.3]
LESSER_FLOAT = -5.4
GREATER_FLOAT = 6.1
DISJOINT_FLOAT_RANGE = [7.3, 10.2]

FLOAT_TEST_PARAMETERS = [
    ("__lte", FLOAT_TEST_ITEMS[1], [0, 1]),
    ("__gte", FLOAT_TEST_ITEMS[1], [1, 2]),
    ("__range", FLOAT_TEST_ITEMS[0:2], [0, 1]),
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
]

DATETIME_TEST_ITEMS = [
    datetime.datetime(2001, 3, 7, 10, 20, 20, tzinfo=datetime.UTC),
    datetime.datetime(2002, 6, 13, 11, 30, 30, tzinfo=datetime.UTC),
    datetime.datetime(2003, 8, 15, 12, 40, 40, tzinfo=datetime.UTC),
]
LESSER_DATETIME = datetime.datetime(1990, 2, 5, 5, 10, 10, tzinfo=datetime.UTC)
GREATER_DATETIME = datetime.datetime(2020, 10, 24, 20, 50, 50, tzinfo=datetime.UTC)
DISJOINT_DATETIME_RANGE = [
    datetime.datetime(2020, 10, 24, 20, 50, 50, tzinfo=datetime.UTC),
    datetime.datetime(2021, 11, 28, 21, 55, 55, tzinfo=datetime.UTC),
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
]


@pytest.fixture(scope="package")
def unblocked_db(django_db_setup, django_db_blocker):
    """Fixture safely unblocking the database for scoped db fixtures."""
    with django_db_blocker.unblock():
        yield
        call_command("flush", "--no-input")


@pytest.fixture(scope="package")
def account_queryset(unblocked_db, pkg_monkeypatch):
    """Fixture adding accounts with the test attributes to the database and returns them in a queryset."""
    for number, text_test_item in enumerate(TEXT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            account = baker.prepare(
                Account,
                mail_address=text_test_item,
                mail_host=text_test_item,
                mail_host_port=INT_TEST_ITEMS[number],
                timeout=FLOAT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                is_healthy=BOOL_TEST_ITEMS[number],
                last_error=text_test_item,
                last_error_occurred_at=DATETIME_TEST_ITEMS[number],
                _save_related=True,
            )
            pkg_monkeypatch.setattr(account, "update_mailboxes", lambda: None)
            account.save()
            pkg_monkeypatch.undo()

    return Account.objects.all()


@pytest.fixture(scope="package")
def mailbox_queryset(unblocked_db, account_queryset):
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
                last_error=text_test_item,
                last_error_occurred_at=DATETIME_TEST_ITEMS[number],
                account=account_queryset.get(id=number + 1),
            )

    return Mailbox.objects.all()


@pytest.fixture(scope="package")
def daemon_queryset(unblocked_db, mailbox_queryset):
    """Fixture adding daemons with the test attributes to the database and returns them in a queryset."""
    for number, bool_test_item in enumerate(BOOL_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            interval = baker.make(
                IntervalSchedule,
                every=INT_TEST_ITEMS[number],
                period=IntervalSchedule.PERIOD_CHOICES[number],
            )
            celery_task = baker.make(
                PeriodicTask,
                interval=interval,
                enabled=bool_test_item,
                total_run_count=INT_TEST_ITEMS[number],
            )
            daemon = baker.make(
                Daemon,
                interval=interval,
                fetching_criterion_arg=TEXT_TEST_ITEMS[number],
                is_healthy=bool_test_item,
                last_error=TEXT_TEST_ITEMS[number],
                last_error_occurred_at=DATETIME_TEST_ITEMS[number],
                mailbox=mailbox_queryset.get(id=number + 1),
            )
            daemon.celery_task = celery_task
            daemon.save(update_fields=["celery_task"])

    return Daemon.objects.all()


@pytest.fixture(scope="package")
def correspondent_queryset(
    unblocked_db,
):
    """Fixture adding correspondents with the test attributes to the database and returns them in a queryset."""
    for number, text_test_item in enumerate(TEXT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                Correspondent,
                email_name=text_test_item,
                real_name=text_test_item,
                email_address=text_test_item,
                list_id=text_test_item,
                list_owner=text_test_item,
                list_subscribe=text_test_item,
                list_unsubscribe=text_test_item,
                list_unsubscribe_post=text_test_item,
                list_post=text_test_item,
                list_help=text_test_item,
                list_archive=text_test_item,
                is_favorite=BOOL_TEST_ITEMS[number],
            )

    return Correspondent.objects.all()


@pytest.fixture(scope="package")
def email_queryset(
    unblocked_db,
    mailbox_queryset,
    correspondent_queryset,
):
    """Fixture adding emails with the test attributes to the database and returns them in a queryset."""
    for number, text_test_item in enumerate(TEXT_TEST_ITEMS):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            new_email = baker.make(
                Email,
                message_id=text_test_item,
                datetime=datetime.datetime.now(tz=datetime.UTC),
                subject=text_test_item,
                plain_bodytext=text_test_item,
                html_bodytext=text_test_item,
                datasize=INT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                mailbox=mailbox_queryset.get(id=number + 1),
                x_spam_flag=BOOL_TEST_ITEMS[number],
            )
            baker.make(
                EmailCorrespondent,
                email=new_email,
                correspondent=correspondent_queryset.get(id=number + 1),
            )

    return Email.objects.all()


@pytest.fixture(scope="package")
def attachment_queryset(unblocked_db, email_queryset):
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
