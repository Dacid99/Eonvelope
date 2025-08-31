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

"""Test module for :mod:`core.models.Daemon`."""

import datetime
import json
from uuid import UUID

import pytest
from django.db import IntegrityError
from django.urls import reverse
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from model_bakery import baker

from core import constants
from core.models import Daemon, Mailbox
from core.utils.fetchers.exceptions import MailAccountError, MailboxError


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """The mocked :attr:`core.models.Daemon.logger`."""
    return mocker.patch("core.models.Daemon.logger", autospec=True)


@pytest.fixture
def mock_Mailbox_fetch(mocker):
    """Patches `core.models.Mailbox.fetch`."""
    return mocker.patch("core.models.Mailbox.Mailbox.fetch")


@pytest.fixture
def mock_celery_app(mocker):
    """Patches the celery current app."""
    return mocker.patch("core.models.Daemon.current_app", autospec=True)


@pytest.mark.django_db
def test_Daemon_fields(fake_daemon):
    """Tests the fields of :class:`core.models.Daemon.Daemon`."""
    assert fake_daemon.uuid is not None
    assert isinstance(fake_daemon.uuid, UUID)
    assert fake_daemon.mailbox is not None
    assert isinstance(fake_daemon.mailbox, Mailbox)
    assert fake_daemon.fetching_criterion == constants.EmailFetchingCriterionChoices.ALL
    assert fake_daemon.interval is not None
    assert fake_daemon.is_healthy is None
    assert fake_daemon.last_error is not None
    assert fake_daemon.updated is not None
    assert isinstance(fake_daemon.updated, datetime.datetime)
    assert fake_daemon.created is not None
    assert isinstance(fake_daemon.created, datetime.datetime)


@pytest.mark.django_db
def test_Daemon___str__(fake_daemon):
    """Tests the string representation of :class:`core.models.Daemon.Daemon`."""
    assert str(fake_daemon.uuid) in str(fake_daemon)
    assert str(fake_daemon.mailbox) in str(fake_daemon)


@pytest.mark.django_db
def test_Daemon_foreign_key_deletion(fake_daemon):
    """Tests the on_delete foreign key constraint in :class:`core.models.Daemon.Daemon`."""
    assert fake_daemon is not None

    fake_daemon.mailbox.delete()

    with pytest.raises(Daemon.DoesNotExist):
        fake_daemon.refresh_from_db()


@pytest.mark.django_db
def test_Daemon_unique_together_constraint_mailbox_fetching_criterion(
    faker, fake_daemon
):
    """Tests the unique together constraint on :attr:`core.models.Daemon.Daemon.mailbox` and :attr:`core.models.Daemon.Daemon.fetching_criterion` of :class:`core.models.Daemon.Daemon`."""
    with pytest.raises(IntegrityError):
        baker.make(
            Daemon,
            mailbox=fake_daemon.mailbox,
            fetching_criterion=fake_daemon.fetching_criterion,
        )


@pytest.mark.django_db
def test_Daemon_valid_fetching_criterion_constraint(faker, fake_daemon):
    """Tests the constraint on :attr:`core.models.Daemon.Daemon.fetching_criterion` of :class:`core.models.Daemon.Daemon`."""
    with pytest.raises(IntegrityError):
        baker.make(
            Daemon,
            mailbox=fake_daemon.mailbox,
            fetching_criterion="BAD_CRITERION",
        )


@pytest.mark.django_db
def test_Daemon_save_new(fake_mailbox):
    """Tests :func:`core.models.Correspondent.Correspondent.delete`
    in case the interval was changed.
    """
    new_interval = baker.make(IntervalSchedule)
    new_daemon = baker.prepare(Daemon, interval=new_interval, mailbox=fake_mailbox)
    new_daemon.celery_task = None

    new_daemon.save()

    new_daemon.refresh_from_db()
    assert new_daemon.celery_task
    assert isinstance(new_daemon.celery_task, PeriodicTask)
    assert new_daemon.celery_task.interval == new_daemon.interval
    assert new_daemon.celery_task.task == "core.tasks.fetch_emails"
    assert new_daemon.celery_task.args == json.dumps([str(new_daemon.uuid)])


@pytest.mark.django_db
def test_Daemon_save_updated_interval(fake_daemon):
    """Tests :func:`core.models.Correspondent.Correspondent.delete`
    in case the interval was changed.
    """
    new_interval = baker.make(IntervalSchedule)
    fake_daemon.interval = new_interval

    assert fake_daemon.celery_task.interval != new_interval

    fake_daemon.save()

    assert fake_daemon.celery_task.interval == new_interval


@pytest.mark.django_db
def test_Daemon_delete_celery_task_deletion(fake_daemon):
    """Tests :func:`core.models.Correspondent.Correspondent.delete`
    in case there is a celery_task.
    """
    daemon_task = fake_daemon.celery_task

    assert daemon_task is not None

    fake_daemon.delete()

    with pytest.raises(daemon_task.__class__.DoesNotExist):
        daemon_task.refresh_from_db()


@pytest.mark.django_db
def test_Daemon_delete_no_celery_task(fake_daemon):
    """Tests :func:`core.models.Correspondent.Correspondent.delete`
    in case there is a celery_task.
    """
    fake_daemon.celery_task = None

    fake_daemon.delete()
    # check that there's no attempt to delete the None-task that would raise


@pytest.mark.django_db
def test_Daemon_test_success(mock_celery_app, fake_daemon):
    """Tests :func:`core.models.Daemon.Daemon.test`
    in case of success.
    """
    fake_daemon.test()
    args = json.loads(fake_daemon.celery_task.args or "[]")
    kwargs = json.loads(fake_daemon.celery_task.kwargs or "{}")

    mock_celery_app.send_task.assert_called_once_with(
        "core.tasks.fetch_emails", args=args, kwargs=kwargs
    )
    mock_celery_app.send_task.return_value.get.assert_called_once_with()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "error", [AssertionError, ValueError, MailAccountError, MailboxError]
)
def test_Daemon_test_failure(mock_celery_app, fake_daemon, error):
    """Tests :func:`core.models.Daemon.Daemon.test`
    in case of failure.
    """
    mock_celery_app.send_task.return_value.get.side_effect = error(Exception())
    args = json.loads(fake_daemon.celery_task.args or "[]")
    kwargs = json.loads(fake_daemon.celery_task.kwargs or "{}")

    with pytest.raises(error):
        fake_daemon.test()

    mock_celery_app.send_task.assert_called_once_with(
        "core.tasks.fetch_emails", args=args, kwargs=kwargs
    )
    mock_celery_app.send_task.return_value.get.assert_called_once_with()


@pytest.mark.django_db
def test_Daemon_get_absolute_url(fake_daemon):
    """Tests :func:`core.models.Daemon.Daemon.get_absolute_url`."""
    result = fake_daemon.get_absolute_url()

    assert result == reverse(
        f"web:{fake_daemon.BASENAME}-detail",
        kwargs={"pk": fake_daemon.pk},
    )


@pytest.mark.django_db
def test_Daemon_get_absolute_edit_url(fake_daemon):
    """Tests :func:`core.models.Daemon.Daemon.get_absolute_edit_url`."""
    result = fake_daemon.get_absolute_edit_url()

    assert result == reverse(
        f"web:{fake_daemon.BASENAME}-edit",
        kwargs={"pk": fake_daemon.pk},
    )


@pytest.mark.django_db
def test_Daemon_get_absolute_list_url(fake_daemon):
    """Tests :func:`core.models.Daemon.Daemon.get_absolute_list_url`."""
    result = fake_daemon.get_absolute_list_url()

    assert result == reverse(
        f"web:{fake_daemon.BASENAME}-filter-list",
    )
