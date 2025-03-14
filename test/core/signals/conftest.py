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

"""Conftest file for :mod:`core.signals`."""

import pytest
from model_bakery import baker

from core.models.DaemonModel import DaemonModel
from core.models.MailboxModel import MailboxModel


@pytest.fixture
def accountModel_with_mailboxes(accountModel, mailboxModel):
    baker.make(MailboxModel, account=accountModel)
    return accountModel


@pytest.fixture
def mailboxModel_with_daemons(faker, mailboxModel, daemonModel):
    """Fixture for a :class:`core.models.MailboxModel.MailboxModel` with daemons and a account."""
    baker.make(
        DaemonModel,
        mailbox=mailboxModel,
        log_filepath=faker.file_path(extension="log"),
    )
    return mailboxModel
