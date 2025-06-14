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

"""Test module for :mod:`core.models.Daemon`."""

import datetime
import logging
import logging.handlers
import os
from uuid import UUID

import pytest
from django.db import IntegrityError
from django.urls import reverse
from model_bakery import baker

from core import constants
from core.models import Daemon, Mailbox
from Emailkasten.utils.workarounds import get_config


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Mocks the :attr:`core.models.Daemon.logger`.

    Returns:
        The mocked logger instance.
    """
    return mocker.patch("core.models.Daemon.logger", autospec=True)


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
    assert fake_daemon.log_filepath is not None
    assert fake_daemon.log_backup_count == get_config("DAEMON_LOG_BACKUP_COUNT_DEFAULT")
    assert fake_daemon.logfile_size == get_config("DAEMON_LOGFILE_SIZE_DEFAULT")
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
def test_Daemon_unique_constraint_log_filepath(fake_daemon):
    """Tests the unique constraints on :attr:`core.models.Daemon.Daemon.log_filepath` of :class:`core.models.Daemon.Daemon`."""
    with pytest.raises(IntegrityError):
        baker.make(Daemon, log_filepath=fake_daemon.log_filepath)


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
            log_filepath=faker.file_path(extension="log"),
        )


@pytest.mark.django_db
def test_Daemon_save_logfile_creation(settings, fake_fs, fake_daemon):
    """Tests :func:`core.models.Correspondent.Correspondent.save`
    in case there is no log_filepath.
    """
    fake_daemon.log_filepath = None

    fake_daemon.save()

    fake_daemon.refresh_from_db()
    assert os.path.dirname(fake_daemon.log_filepath) == str(settings.LOG_DIRECTORY_PATH)
    logger = logging.getLogger(str(fake_daemon.uuid))
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.handlers.RotatingFileHandler)
    assert logger.handlers[0].baseFilename == fake_daemon.log_filepath
    assert logger.handlers[0].backupCount == fake_daemon.log_backup_count
    assert logger.handlers[0].maxBytes == fake_daemon.logfile_size


@pytest.mark.django_db
@pytest.mark.parametrize(
    "log_filepath, expected_has_download",
    [
        (None, False),
        ("some/log/file/path", True),
    ],
)
def test_Daemon_has_download(fake_daemon, log_filepath, expected_has_download):
    """Tests :func:`core.models.Daemon.Daemon.has_download` in the two relevant cases."""
    fake_daemon.log_filepath = log_filepath

    result = fake_daemon.has_download

    assert result == expected_has_download


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
