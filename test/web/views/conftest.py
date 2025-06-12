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

"""File with fixtures required for all viewset tests. Automatically imported to test_ files.

The viewset tests are made against a mocked consistent database with an instance of every model in every testcase.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.urls import reverse


if TYPE_CHECKING:
    from collections.abc import Callable

    from django.db.models import Model
    from django.test.client import Client
    from rest_framework.viewsets import ModelViewSet


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
    fake_mailing_list,
):
    """Fixture providing a complete database setup."""


@pytest.fixture
def other_client(client, other_user) -> Client:
    """Fixture creating a :class:`django.test.client.Client` instance that is authenticated as :attr:`other_user`.

    Returns:
        The authenticated Client.
    """
    client.force_login(user=other_user)
    return client


@pytest.fixture
def owner_client(client, owner_user) -> Client:
    """Fixture creating a :class:`django.test.client.Client` instance that is authenticated as :attr:`owner_user`.

    Returns:
        The authenticated Client.
    """
    client.force_login(user=owner_user)
    return client


@pytest.fixture(scope="package")
def login_url() -> str:
    """Fixture with the login url.

    Returns:
        The login url.
    """
    return reverse("account_login")


@pytest.fixture(scope="package")
def list_url() -> Callable[[type[ModelViewSet]], str]:
    """Fixture getting the viewsets url for list actions.

    Returns:
        The list url.
    """
    return lambda view_class: reverse(f"web:{view_class.URL_NAME}")


@pytest.fixture(scope="package")
def detail_url() -> Callable[[type[ModelViewSet], Model], str]:
    """Fixture getting the viewsets url for detail actions.

    Returns:
        The detail url.
    """
    return lambda view_class, instance: reverse(
        f"web:{view_class.URL_NAME}", args=[instance.id]
    )


@pytest.fixture(scope="package")
def custom_list_action_url() -> Callable[[type[ModelViewSet], str], str]:
    """Fixture getting the viewsets url for custom list actions.

    Returns:
        A callable that gets the list url of the viewset from the custom action name.
    """
    return lambda view_class, custom_list_action_url_name: (
        reverse(f"web:{view_class.URL_NAME}-{custom_list_action_url_name}")
    )


@pytest.fixture(scope="package")
def custom_detail_action_url() -> Callable[[type[ModelViewSet], str, Model], str]:
    """Fixture getting the viewsets url for custom detail actions.

    Returns:
        A callable that gets the detail url of the viewset from the custom action name.
    """
    return lambda view_class, custom_detail_action_url_name, instance: (
        reverse(
            f"web:{view_class.URL_NAME}-{custom_detail_action_url_name}",
            args=[instance.id],
        )
    )


@pytest.fixture
def mock_Account_test_connection(mocker):
    """Patches :func:`core.models.Account.Account.test_connection` for testing of the test action."""
    return mocker.patch(
        "core.models.Account.Account.test_connection",
        autospec=True,
    )


@pytest.fixture
def mock_Account_update_mailboxes(mocker):
    """Patches :func:`core.models.Account.Account.update_mailboxes` for testing of the test action."""
    return mocker.patch(
        "core.models.Account.Account.update_mailboxes",
        autospec=True,
    )


@pytest.fixture
def mock_Mailbox_test_connection(mocker):
    """Patches :func:`core.models.Mailbox.Mailbox.test_connection` for testing of the test action."""
    return mocker.patch(
        "core.models.Mailbox.Mailbox.test_connection",
        autospec=True,
    )


@pytest.fixture
def mock_Mailbox_fetch(mocker):
    """Patches :func:`core.models.Mailbox.Mailbox.fetch` for testing of the test action."""
    return mocker.patch(
        "core.models.Mailbox.Mailbox.fetch",
        autospec=True,
    )
