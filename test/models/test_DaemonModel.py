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

"""Test module for :mod:`Emailkasten.Models.DaemonModel`."""

import datetime

import pytest
from django.db import IntegrityError
from model_bakery import baker

from Emailkasten import constants
from Emailkasten.Models.DaemonModel import DaemonModel
from Emailkasten.Models.MailboxModel import MailboxModel


@pytest.mark.django_db
def test_DaemonModel_creation():
    """Tests the correct default creation of :class:`Emailkasten.Models.DaemonModel.DaemonModel`."""

    daemon = baker.make(DaemonModel)
    assert daemon.uuid is not None
    assert isinstance(daemon.uuid, str)
    assert daemon.mailbox is not None
    assert isinstance(daemon.mailbox, MailboxModel)
    assert daemon.fetching_criterion is constants.MailFetchingCriteria.ALL
    assert daemon.cycle_interval is constants.EMailArchiverDaemonConfiguration.CYCLE_PERIOD_DEFAULT
    assert daemon.is_running is False
    assert daemon.is_healthy is True
    assert daemon.log_filepath is not None

    assert daemon.updated is not None
    assert isinstance(daemon.updated, datetime.datetime)
    assert daemon.created is not None
    assert isinstance(daemon.created, datetime.datetime)

    assert daemon.uuid in str(daemon)
    assert str(daemon.mailbox) in str(daemon)


@pytest.mark.django_db
def test_MailboxModel_foreign_key_deletion():
    """Tests the on_delete foreign key constraint in :class:`Emailkasten.Models.AccountModel.AccountModel`."""

    mailbox = baker.make(MailboxModel)
    daemon = baker.make(DaemonModel, mailbox = mailbox)
    assert daemon is not None
    mailbox.delete()
    with pytest.raises(DaemonModel.DoesNotExist):
        daemon.refresh_from_db()


@pytest.mark.django_db
def test_DaemonModel_unique():
    """Tests the unique constraints of :class:`Emailkasten.Models.DaemonModel.DaemonModel`."""

    baker.make(DaemonModel, uuid="abc123")
    with pytest.raises(IntegrityError):
        baker.make(DaemonModel, uuid="abc123")

    baker.make(DaemonModel, log_filepath="test")
    with pytest.raises(IntegrityError):
        baker.make(DaemonModel, log_filepath="test")
