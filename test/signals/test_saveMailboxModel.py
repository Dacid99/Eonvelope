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

"""Test file for :mod:`Emailkasten.signals.saveMailboxModel`."""

import pytest
from model_bakery import baker

from Emailkasten.Models.DaemonModel import DaemonModel
from Emailkasten.Models.MailboxModel import MailboxModel

@pytest.mark.django_db
def test_MailboxModel_post_save():
    """Tests behaviour of :func:`Emailkasten.signals.saveMailboxModel.post_save_is_healthy`."""
    mailbox = baker.make(MailboxModel)
    daemon_1 = baker.make(DaemonModel, mailbox=mailbox)
    daemon_2 = baker.make(DaemonModel, mailbox=mailbox)

    assert mailbox.account.is_healthy is True

    mailbox.is_healthy = False
    mailbox.save(update_fields = ['is_healthy'])
    daemons = mailbox.daemons.all()
    for daemon in daemons:
        assert daemon.is_healthy is False

    mailbox.is_healthy = True
    mailbox.save(update_fields = ['is_healthy'])
    for daemon in daemons:
        daemon.refresh_from_db()
        assert daemon.is_healthy is False
