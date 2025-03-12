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

"""Test file for :mod:`core.signals.save_MailboxModel`."""

import pytest
from model_bakery import baker

from core.models.AccountModel import AccountModel
from core.models.DaemonModel import DaemonModel
from core.models.MailboxModel import MailboxModel

from .test_save_DaemonModel import mock_updateDaemon


@pytest.fixture
def mailboxModel(faker):
    """Fixture for a :class:`core.models.MailboxModel.MailboxModel` with daemons and a account."""
    account = baker.make(AccountModel)
    mailbox = baker.make(MailboxModel, account=account)
    baker.make(
        DaemonModel, mailbox=mailbox, log_filepath=faker.file_path(extension="log")
    )
    baker.make(
        DaemonModel, mailbox=mailbox, log_filepath=faker.file_path(extension="log")
    )
    return mailbox


@pytest.mark.django_db
@pytest.mark.parametrize(
    "account_is_healthy, mailbox_is_healthy, daemons_is_healthy",
    [
        (True, False, True),
        (False, True, True),
        (False, True, False),
        (False, False, True),
    ],
)
def test_illegal_states(
    mailboxModel,
    mock_updateDaemon,
    account_is_healthy,
    mailbox_is_healthy,
    daemons_is_healthy,
):
    """Tests for existance of states that are impossible under the is_healthy signal chain."""
    mailboxModel.account.is_healthy = account_is_healthy
    mailboxModel.account.save(update_fields=["is_healthy"])
    mailboxModel.refresh_from_db()
    mailboxModel.is_healthy = mailbox_is_healthy
    mailboxModel.save(update_fields=["is_healthy"])
    for daemon in mailboxModel.daemons.all():
        daemon.is_healthy = daemons_is_healthy
        daemon.save(update_fields=["is_healthy"])

    mailboxModel.refresh_from_db()
    with pytest.raises(AssertionError):
        assert mailboxModel.account.is_healthy is account_is_healthy
        assert mailboxModel.is_healthy is mailbox_is_healthy
        for daemon in mailboxModel.daemons.all():
            assert daemon.is_healthy is daemons_is_healthy


@pytest.mark.django_db
@pytest.mark.parametrize(
    "account_is_healthy_start, mailbox_is_healthy_start, daemons_is_healthy_start, account_is_healthy_end, mailbox_is_healthy_end, daemons_is_healthy_end",
    [
        (True, True, True, False, False, False),
        (True, True, False, False, False, False),
        (True, False, False, False, False, False),
        (False, False, False, True, False, False),
    ],
)
def test_toggle_AccountModel_is_healthy(
    mailboxModel,
    mock_updateDaemon,
    account_is_healthy_start,
    mailbox_is_healthy_start,
    daemons_is_healthy_start,
    account_is_healthy_end,
    mailbox_is_healthy_end,
    daemons_is_healthy_end,
):
    """Tests the expected propagation of health states through the models
    if :attr:`core.models.AccountModel.AccountModel.is_healthy` is changed.
    """
    mailboxModel.account.is_healthy = account_is_healthy_start
    mailboxModel.account.save(update_fields=["is_healthy"])
    mailboxModel.refresh_from_db()
    mailboxModel.is_healthy = mailbox_is_healthy_start
    mailboxModel.save(update_fields=["is_healthy"])
    for daemon in mailboxModel.daemons.all():
        daemon.is_healthy = daemons_is_healthy_start
        daemon.save(update_fields=["is_healthy"])

    assert mailboxModel.account.is_healthy is account_is_healthy_start
    assert mailboxModel.is_healthy is mailbox_is_healthy_start
    for daemon in mailboxModel.daemons.all():
        assert daemon.is_healthy is daemons_is_healthy_start

    mailboxModel.account.is_healthy = not mailboxModel.account.is_healthy
    mailboxModel.account.save(update_fields=["is_healthy"])

    mailboxModel.refresh_from_db()
    for daemon in mailboxModel.daemons.all():
        daemon.refresh_from_db()
        assert daemon.is_healthy is daemons_is_healthy_end
    assert mailboxModel.is_healthy is mailbox_is_healthy_end
    assert mailboxModel.account.is_healthy is account_is_healthy_end


@pytest.mark.django_db
@pytest.mark.parametrize(
    "account_is_healthy_start, mailbox_is_healthy_start, daemons_is_healthy_start, account_is_healthy_end, mailbox_is_healthy_end, daemons_is_healthy_end",
    [
        (True, True, True, True, False, False),
        (True, True, False, True, False, False),
        (True, False, False, True, True, False),
        (False, False, False, True, True, False),
    ],
)
def test_toggle_MailboxModel_is_healthy(
    mailboxModel,
    mock_updateDaemon,
    account_is_healthy_start,
    mailbox_is_healthy_start,
    daemons_is_healthy_start,
    account_is_healthy_end,
    mailbox_is_healthy_end,
    daemons_is_healthy_end,
):
    """Tests the expected propagation of health states through the models
    if :attr:`core.models.MailboxModel.MailboxModel.is_healthy` is changed.
    """
    mailboxModel.account.is_healthy = account_is_healthy_start
    mailboxModel.account.save(update_fields=["is_healthy"])
    mailboxModel.refresh_from_db()
    mailboxModel.is_healthy = mailbox_is_healthy_start
    mailboxModel.save(update_fields=["is_healthy"])
    for daemon in mailboxModel.daemons.all():
        daemon.is_healthy = daemons_is_healthy_start
        daemon.save(update_fields=["is_healthy"])

    assert mailboxModel.account.is_healthy is account_is_healthy_start
    assert mailboxModel.is_healthy is mailbox_is_healthy_start
    for daemon in mailboxModel.daemons.all():
        assert daemon.is_healthy is daemons_is_healthy_start

    mailboxModel.is_healthy = not mailboxModel.is_healthy
    mailboxModel.save(update_fields=["is_healthy"])

    mailboxModel.refresh_from_db()
    daemons = mailboxModel.daemons.all()
    for daemon in daemons:
        assert daemon.is_healthy is daemons_is_healthy_end
    assert mailboxModel.is_healthy is mailbox_is_healthy_end
    assert mailboxModel.account.is_healthy is account_is_healthy_end


@pytest.mark.django_db
@pytest.mark.parametrize(
    "account_is_healthy_start, mailbox_is_healthy_start, daemons_is_healthy_start, account_is_healthy_end, mailbox_is_healthy_end, daemons_is_healthy_end",
    [
        (True, True, True, True, True, False),
        (True, True, False, True, True, True),
        (True, False, False, True, True, True),
        (False, False, False, True, True, True),
    ],
)
def test_toggle_DaemonModel_is_healthy(
    mailboxModel,
    mock_updateDaemon,
    account_is_healthy_start,
    mailbox_is_healthy_start,
    daemons_is_healthy_start,
    account_is_healthy_end,
    mailbox_is_healthy_end,
    daemons_is_healthy_end,
):
    """Tests the expected propagation of health states through the models
    if :attr:`core.models.DaemonModel.DaemonModel.is_healthy` is changed.
    """
    mailboxModel.account.is_healthy = account_is_healthy_start
    mailboxModel.account.save(update_fields=["is_healthy"])
    mailboxModel.refresh_from_db()
    mailboxModel.is_healthy = mailbox_is_healthy_start
    mailboxModel.save(update_fields=["is_healthy"])
    for daemon in mailboxModel.daemons.all():
        daemon.is_healthy = daemons_is_healthy_start
        daemon.save(update_fields=["is_healthy"])

    assert mailboxModel.account.is_healthy is account_is_healthy_start
    assert mailboxModel.is_healthy is mailbox_is_healthy_start
    for daemon in mailboxModel.daemons.all():
        assert daemon.is_healthy is daemons_is_healthy_start

    for daemon in mailboxModel.daemons.all():
        daemon.is_healthy = not daemon.is_healthy
        daemon.save(update_fields=["is_healthy"])

    mailboxModel.refresh_from_db()
    daemons = mailboxModel.daemons.all()
    for daemon in daemons:
        assert daemon.is_healthy is daemons_is_healthy_end
    assert mailboxModel.is_healthy is mailbox_is_healthy_end
    assert mailboxModel.account.is_healthy is account_is_healthy_end
