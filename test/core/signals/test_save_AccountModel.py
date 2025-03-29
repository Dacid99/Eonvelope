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

from core.models.MailboxModel import MailboxModel


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Mocks :attr:`core.signals.save_AccountModel.logger` of the module."""
    return mocker.patch("core.signals.save_AccountModel.logger", autospec=True)


@pytest.mark.django_db
def test_AccountModel_post_save_from_healthy(mock_logger, accountModel_with_mailboxes):
    """Tests the post_save function of :class:`core.models.AccountModel.AccountModel`."""
    accountModel_with_mailboxes.is_healthy = True
    accountModel_with_mailboxes.save(update_fields=["is_healthy"])
    for mailbox in accountModel_with_mailboxes.mailboxes.all():
        mailbox.is_healthy = True
        mailbox.save(update_fields=["is_healthy"])

    accountModel_with_mailboxes.refresh_from_db()
    assert accountModel_with_mailboxes.is_healthy is True
    for mailbox in accountModel_with_mailboxes.mailboxes.all():
        mailbox.refresh_from_db()
        assert mailbox.is_healthy is True

    accountModel_with_mailboxes.is_healthy = False
    accountModel_with_mailboxes.save(update_fields=["is_healthy"])

    accountModel_with_mailboxes.refresh_from_db()
    assert accountModel_with_mailboxes.is_healthy is False
    for mailbox in accountModel_with_mailboxes.mailboxes.all():
        mailbox.refresh_from_db()
        assert mailbox.is_healthy is False
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_AccountModel_post_save_from_unhealthy(
    accountModel_with_mailboxes, mock_logger
):
    """Tests the post_save function of :class:`core.models.AccountModel.AccountModel`."""
    accountModel_with_mailboxes.is_healthy = False
    accountModel_with_mailboxes.save(update_fields=["is_healthy"])
    for mailbox in accountModel_with_mailboxes.mailboxes.all():
        mailbox.is_healthy = False
        mailbox.save(update_fields=["is_healthy"])

    accountModel_with_mailboxes.refresh_from_db()
    assert accountModel_with_mailboxes.is_healthy is False
    for mailbox in accountModel_with_mailboxes.mailboxes.all():
        mailbox.refresh_from_db()
        assert mailbox.is_healthy is False

    accountModel_with_mailboxes.is_healthy = True
    accountModel_with_mailboxes.save(update_fields=["is_healthy"])

    accountModel_with_mailboxes.refresh_from_db()
    assert accountModel_with_mailboxes.is_healthy is True
    for mailbox in accountModel_with_mailboxes.mailboxes.all():
        mailbox.refresh_from_db()
        assert mailbox.is_healthy is False
    mock_logger.debug.assert_called()
