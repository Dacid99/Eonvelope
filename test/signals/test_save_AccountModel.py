# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Test module for :mod:`Emailkasten.signals.save_AccountModel`."""

import pytest
from model_bakery import baker

from Emailkasten.Models.AccountModel import AccountModel
from Emailkasten.Models.MailboxModel import MailboxModel

@pytest.mark.django_db
def test_AccountModel_post_save_is_healthy():
    """Tests the post_save function of :class:`Emailkasten.Models.AccountModel.AccountModel`."""

    account = baker.make(AccountModel)

    mailbox_1 = baker.make(MailboxModel, account=account)
    mailbox_2 = baker.make(MailboxModel, account=account)

    assert mailbox_1.is_healthy is True
    assert mailbox_2.is_healthy is True

    account.is_healthy = False
    account.save(update_fields = ['is_healthy'])
    mailbox_1.refresh_from_db()
    mailbox_2.refresh_from_db()
    assert mailbox_1.is_healthy is False
    assert mailbox_2.is_healthy is False

    account.is_healthy = True
    account.save(update_fields = ['is_healthy'])
    mailbox_1.refresh_from_db()
    mailbox_2.refresh_from_db()
    assert mailbox_1.is_healthy is False
    assert mailbox_2.is_healthy is False
