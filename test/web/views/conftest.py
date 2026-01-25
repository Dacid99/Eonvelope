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

"""File with fixtures required for all viewset tests. Automatically imported to `test_` files.

The viewset tests are made against a mocked consistent database with an instance of every model in every testcase.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def complete_database(
    owner_user,
    other_user,
    fake_account,
    fake_attachment,
    fake_correspondent,
    fake_daemon,
    fake_email,
    fake_emailcorrespondent,
    fake_mailbox,
):
    """Fixture providing a complete database setup."""


@pytest.fixture
def mock_Mailbox_test(mocker):
    """Patches :func:`core.models.Mailbox.Mailbox.test` for testing of the test action."""
    return mocker.patch(
        "core.models.Mailbox.Mailbox.test",
        autospec=True,
    )


@pytest.fixture
def mock_Mailbox_fetch(mocker):
    """Patches :func:`core.models.Mailbox.Mailbox.fetch` for testing of the test action."""
    return mocker.patch(
        "core.models.Mailbox.Mailbox.fetch",
        autospec=True,
    )


@pytest.fixture
def mock_Daemon_test(mocker):
    """Patches :func:`core.models.Daemon.Daemon.test` for testing of the test action."""
    return mocker.patch("core.models.Daemon.Daemon.test", autospec=True)


@pytest.fixture
def mock_Attachment_share_to_paperless(mocker):
    """Patches `core.models.Attachment.share_to_paperless`."""
    return mocker.patch(
        "core.models.Attachment.Attachment.share_to_paperless", autospec=True
    )


@pytest.fixture
def mock_Attachment_share_to_immich(mocker):
    """Patches `core.models.Attachment.share_to_immich`."""
    return mocker.patch(
        "core.models.Attachment.Attachment.share_to_immich", autospec=True
    )


@pytest.fixture
def mock_Correspondent_share_to_nextcloud(mocker):
    """Patches `core.models.Correspondent.share_to_nextcloud`."""
    return mocker.patch(
        "core.models.Correspondent.Correspondent.share_to_nextcloud", autospec=True
    )


@pytest.fixture
def mock_Email_restore_to_mailbox(mocker):
    """Patches `core.models.Email.restore_to_mailbox`."""
    return mocker.patch("core.models.Email.Email.restore_to_mailbox")


@pytest.fixture
def mock_Email_reprocess(mocker):
    """Patches `core.models.Email.reprocess`."""
    return mocker.patch("core.models.Email.Email.reprocess")
