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

"""Conftest file for :mod:`core.signals`."""

import pytest
from model_bakery import baker

from core.constants import EmailFetchingCriterionChoices
from core.models import Daemon, Mailbox


@pytest.fixture
def account_with_mailboxes(fake_account, fake_mailbox):
    """Fixture adding a mailbox to `account`."""
    baker.make(Mailbox, account=fake_account)
    return fake_account


@pytest.fixture
def mailbox_with_daemons(faker, fake_mailbox, fake_daemon):
    """Fixture adding a daemon to `mailbox`."""
    baker.make(
        Daemon,
        mailbox=fake_mailbox,
        fetching_criterion=EmailFetchingCriterionChoices.NEW.value,
    )
    return fake_mailbox
