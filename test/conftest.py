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

"""File with fixtures and configurations required for all tests. Automatically imported to test_ files.

Test functions generally follow this pattern:

def test_(Classname_methodname)|(functionname)_case(args in order from furthest to closest to this test, e.g. mocker, conftest_fixture, local_fixture, parameter):
    block with
    preparations for the test case

    block with
    pretest-assertions
    confirming the case setup

    block with
    the tested function being executed

    block with
    post-test assertions
    confirming the behaviour of the tested function
"""

from __future__ import annotations

import os
from io import BytesIO
from typing import TYPE_CHECKING

import pytest
from model_bakery import baker

from core.constants import HeaderFields
from core.models.AccountModel import AccountModel
from core.models.AttachmentModel import AttachmentModel
from core.models.CorrespondentModel import CorrespondentModel
from core.models.DaemonModel import DaemonModel
from core.models.EMailCorrespondentsModel import EMailCorrespondentsModel
from core.models.EMailModel import EMailModel
from core.models.MailboxModel import MailboxModel
from core.models.MailingListModel import MailingListModel


if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


def pytest_configure(config) -> None:
    """Configures the path for pytest to be the directory of this file for consistent relative paths."""
    pytest_ini_dir = os.path.dirname(os.path.abspath(config.inifile))
    os.chdir(pytest_ini_dir)


@pytest.fixture
def fake_file_bytes(faker) -> bytes:
    """Fixture providing random bytes to mock file content."""
    return faker.text().encode()


@pytest.fixture
def fake_file(fake_file_bytes) -> BytesIO:
    """Fixture providing a filestream with random content."""
    return BytesIO(fake_file_bytes)


@pytest.fixture
def owner_user(django_user_model) -> AbstractUser:
    """Creates a user that owns the data.

    Returns:
        The owner user instance.
    """
    return baker.make(django_user_model)


@pytest.fixture
def other_user(django_user_model) -> AbstractUser:
    """Creates a user that is not the owner of the data.

    Returns:
       The other user instance.
    """
    return baker.make(django_user_model)


@pytest.fixture
def accountModel(owner_user) -> AccountModel:
    """Creates an :class:`core.models.AccountModel.AccountModel` owned by :attr:`owner_user`.

    Args:
        owner_user: Depends on :func:`owner_user`.

    Returns:
        The account instance for testing.
    """
    return baker.make(AccountModel, user=owner_user)


@pytest.fixture
def mailboxModel(accountModel) -> MailboxModel:
    """Creates an :class:`core.models.MailboxModel.MailboxModel` owned by :attr:`owner_user`.

    Args:
        accountModel: Depends on :func:`accountModel`.

    Returns:
        The mailbox instance for testing.
    """
    return baker.make(MailboxModel, account=accountModel)


@pytest.fixture
def daemonModel(faker, mailboxModel) -> DaemonModel:
    """Creates an :class:`core.models.DaemonModel.DaemonModel` owned by :attr:`owner_user`.

    Args:
        mailboxModel: Depends on :func:`mailboxModel`.

    Returns:
        The daemon instance for testing.
    """
    return baker.make(
        DaemonModel,
        log_filepath=faker.file_path(extension="log"),
        mailbox=mailboxModel,
    )


@pytest.fixture
def correspondentModel() -> CorrespondentModel:
    """Creates an :class:`core.models.CorrespondentModel.CorrespondentModel` owned by :attr:`owner_user`.

    Returns:
        The correspondent instance for testing.
    """
    return baker.make(CorrespondentModel)


@pytest.fixture
def mailingListModel() -> MailingListModel:
    """Creates an :class:`core.models.MailingListModel.MailingListModel` owned by :attr:`owner_user`.

    Returns:
        The mailinglist instance for testing.
    """
    return baker.make(MailingListModel)


@pytest.fixture
def emailModel(faker, correspondentModel, mailboxModel, mailingListModel) -> EMailModel:
    """Creates an :class:`core.models.EMailModel.EMailModel` owned by :attr:`owner_user`.

    Args:
        correspondentModel: Depends on :func:`fixture_correspondentModel`.
        mailboxModel: Depends on :func:`fixture_mailboxModel`.
        mailinglistModel: Depends on :func:`fixture_mailinglistModel`.

    Returns:
        The email instance for testing.
    """
    emailModel = baker.make(
        EMailModel,
        mailbox=mailboxModel,
        mailinglist=mailingListModel,
        eml_filepath=faker.file_path(extension="eml"),
        prerender_filepath=faker.file_path(extension="png"),
    )
    baker.make(
        EMailCorrespondentsModel,
        email=emailModel,
        correspondent=correspondentModel,
        mention=HeaderFields.Correspondents.FROM,
    )
    return emailModel


@pytest.fixture
def attachmentModel(faker, emailModel) -> AttachmentModel:
    """Creates an :class:`core.models.AttachmentModel.AttachmentModel` owned by :attr:`owner_user`.

    Args:
        emailModel: Depends on :func:`fixture_emailModel`.

    Returns:
        The attachment instance for testing.
    """
    return baker.make(
        AttachmentModel, email=emailModel, file_path=faker.file_path(extension="pdf")
    )
