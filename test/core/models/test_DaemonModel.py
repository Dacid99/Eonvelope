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

"""Test module for :mod:`core.models.DaemonModel`."""

import datetime
import os
from uuid import UUID

import pytest
from django.db import IntegrityError
from django.urls import reverse
from model_bakery import baker

from core import constants
from core.models.DaemonModel import DaemonModel
from core.models.MailboxModel import MailboxModel
from Emailkasten.utils.workarounds import get_config


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Mocks the :attr:`core.models.DaemonModel.logger`.

    Returns:
        The mocked logger instance.
    """
    return mocker.patch("core.models.DaemonModel.logger", autospec=True)


@pytest.mark.django_db
def test_DaemonModel_fields(daemonModel):
    """Tests the fields of :class:`core.models.DaemonModel.DaemonModel`."""
    assert daemonModel.uuid is not None
    assert isinstance(daemonModel.uuid, UUID)
    assert daemonModel.mailbox is not None
    assert isinstance(daemonModel.mailbox, MailboxModel)
    assert daemonModel.fetching_criterion == constants.EmailFetchingCriterionChoices.ALL
    assert daemonModel.cycle_interval == get_config("DAEMON_CYCLE_PERIOD_DEFAULT")
    assert daemonModel.restart_time == get_config("DAEMON_RESTART_TIME_DEFAULT")
    assert daemonModel.is_running is False
    assert daemonModel.is_healthy is None
    assert daemonModel.log_filepath is not None
    assert daemonModel.log_backup_count == get_config("DAEMON_LOG_BACKUP_COUNT_DEFAULT")
    assert daemonModel.logfile_size == get_config("DAEMON_LOGFILE_SIZE_DEFAULT")
    assert daemonModel.updated is not None
    assert isinstance(daemonModel.updated, datetime.datetime)
    assert daemonModel.created is not None
    assert isinstance(daemonModel.created, datetime.datetime)


@pytest.mark.django_db
def test_DaemonModel___str__(daemonModel):
    """Tests the string representation of :class:`core.models.DaemonModel.DaemonModel`."""
    assert str(daemonModel.uuid) in str(daemonModel)
    assert str(daemonModel.mailbox) in str(daemonModel)


@pytest.mark.django_db
def test_DaemonModel_foreign_key_deletion(daemonModel):
    """Tests the on_delete foreign key constraint in :class:`core.models.DaemonModel.DaemonModel`."""
    assert daemonModel is not None

    daemonModel.mailbox.delete()

    with pytest.raises(DaemonModel.DoesNotExist):
        daemonModel.refresh_from_db()


@pytest.mark.django_db
def test_DaemonModel_unique_constraints(daemonModel):
    """Tests the unique constraints of :class:`core.models.DaemonModel.DaemonModel`."""
    with pytest.raises(IntegrityError):
        baker.make(DaemonModel, log_filepath=daemonModel.log_filepath)


@pytest.mark.django_db
def test_DaemonModel_save_logfileCreation(faker, settings, daemonModel):
    """Tests :func:`core.models.CorrespondentModel.CorrespondentModel.save`
    in case there is no log_filepath.
    """
    fake_log_directory_path = os.path.dirname(faker.file_path())
    settings.LOG_DIRECTORY_PATH = fake_log_directory_path
    daemonModel.log_filepath = None

    daemonModel.save()

    daemonModel.refresh_from_db()
    assert daemonModel.log_filepath == os.path.join(
        fake_log_directory_path,
        f"daemon_{daemonModel.uuid}.log",
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "log_filepath, expected_has_download",
    [
        (None, False),
        ("some/log/file/path", True),
    ],
)
def test_DaemonModel_has_download(daemonModel, log_filepath, expected_has_download):
    """Tests :func:`core.models.DaemonModel.DaemonModel.has_download` in the two relevant cases."""
    daemonModel.log_filepath = log_filepath

    result = daemonModel.has_download

    assert result == expected_has_download


@pytest.mark.django_db
def test_DaemonModel_get_absolute_url(daemonModel):
    """Tests :func:`core.models.DaemonModel.DaemonModel.get_absolute_url`."""
    result = daemonModel.get_absolute_url()

    assert result == reverse(
        f"web:{daemonModel.BASENAME}-detail",
        kwargs={"pk": daemonModel.pk},
    )


@pytest.mark.django_db
def test_DaemonModel_get_absolute_edit_url(daemonModel):
    """Tests :func:`core.models.DaemonModel.DaemonModel.get_absolute_edit_url`."""
    result = daemonModel.get_absolute_edit_url()

    assert result == reverse(
        f"web:{daemonModel.BASENAME}-edit",
        kwargs={"pk": daemonModel.pk},
    )


@pytest.mark.django_db
def test_DaemonModel_get_absolute_list_url(daemonModel):
    """Tests :func:`core.models.DaemonModel.DaemonModel.get_absolute_list_url`."""
    result = daemonModel.get_absolute_list_url()

    assert result == reverse(
        f"web:{daemonModel.BASENAME}-filter-list",
    )
