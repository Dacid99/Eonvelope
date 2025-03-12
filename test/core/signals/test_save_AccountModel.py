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

"""Test module for :mod:`core.signals.save_AccountModel`."""

import pytest
from model_bakery import baker

from core.models.AccountModel import AccountModel
from core.models.MailboxModel import MailboxModel


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Mocks :attr:`core.signals.save_AccountModel.logger` of the module."""
    return mocker.patch("core.signals.save_AccountModel.logger", autospec=True)


@pytest.mark.django_db
def test_AccountModel_post_save_from_healthy(mock_logger):
    """Tests the post_save function of :class:`core.models.AccountModel.AccountModel`."""

    account = baker.make(AccountModel, is_healthy=True)
    baker.make(MailboxModel, account=account, is_healthy=True, _quantity=2)

    account.is_healthy = False
    account.save(update_fields=["is_healthy"])

    for mailbox in account.mailboxes.all():
        assert mailbox.is_healthy is False
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_AccountModel_post_save_from_unhealthy(mock_logger):
    """Tests the post_save function of :class:`core.models.AccountModel.AccountModel`."""

    account = baker.make(AccountModel, is_healthy=False)
    baker.make(MailboxModel, account=account, is_healthy=False, _quantity=2)

    account.is_healthy = True
    account.save(update_fields=["is_healthy"])

    for mailbox in account.mailboxes.all():
        assert mailbox.is_healthy is False
    mock_logger.debug.assert_not_called()
