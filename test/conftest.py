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
import random
from io import BytesIO
from typing import TYPE_CHECKING

import pytest
from django.forms import model_to_dict
from model_bakery import baker

from core.constants import (
    EmailProtocolChoices,
    HeaderFields,
)
from core.models.AccountModel import AccountModel
from core.models.AttachmentModel import AttachmentModel
from core.models.CorrespondentModel import CorrespondentModel
from core.models.DaemonModel import DaemonModel
from core.models.EMailCorrespondentsModel import EMailCorrespondentsModel
from core.models.EMailModel import EMailModel
from core.models.MailboxModel import MailboxModel
from core.models.MailingListModel import MailingListModel


if TYPE_CHECKING:
    from typing import Any

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
        correspondentModel: Depends on :func:`correspondentModel`.
        mailboxModel: Depends on :func:`mailboxModel`.
        mailinglistModel: Depends on :func:`mailinglistModel`.

    Returns:
        The email instance for testing.
    """
    emailModel = baker.make(
        EMailModel,
        mailbox=mailboxModel,
        mailinglist=mailingListModel,
        eml_filepath=faker.file_path(extension="eml"),
        html_filepath=faker.file_path(extension="png"),
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
        emailModel: Depends on :func:`emailModel`.

    Returns:
        The attachment instance for testing.
    """
    return baker.make(
        AttachmentModel, email=emailModel, file_path=faker.file_path(extension="pdf")
    )


@pytest.fixture
def accountPayload(owner_user) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.AccountModel.AccountModel` payload with data deviating from the defaults.

    Args:
        owner_user: Depends on :func:`owner_user`.

    Returns:
        The clean payload.
    """
    accountData = baker.prepare(
        AccountModel,
        user=owner_user,
        mail_host_port=random.randint(0, 65535),
        protocol=random.choice(EmailProtocolChoices.values),
        timeout=random.randint(1, 1000),
        is_favorite=not AccountModel.is_favorite.field.default,
    )
    payload = model_to_dict(accountData)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.fixture
def attachmentPayload(faker, emailModel) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.AttachmentModel.AttachmentModel` payload with data deviating from the defaults.

    Args:
        emailModel: Depends on :func:`emailModel`.

    Returns:
        The clean payload.
    """
    attachmentData = baker.prepare(
        AttachmentModel,
        email=emailModel,
        content_disposition=faker.name(),
        content_type=faker.name(),
        is_favorite=not AttachmentModel.is_favorite.field.default,
    )
    payload = model_to_dict(attachmentData)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.fixture
def correspondentPayload(faker, emailModel) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.CorrespondentModel.CorrespondentModel` payload with data deviating from the defaults.

    Args:
        emailModel: Depends on :func:`emailModel`.

    Returns:
        The clean payload.
    """
    correspondentData = baker.prepare(
        CorrespondentModel,
        emails=[emailModel],
        email_name=faker.name(),
        is_favorite=not CorrespondentModel.is_favorite.field.default,
    )
    payload = model_to_dict(correspondentData)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.fixture
def daemonPayload(faker, mailboxModel) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.DaemonModel.DaemonModel` payload with data deviating from the defaults.

    Args:
        mailboxModel: Depends on :func:`mailboxModel`.

    Returns:
        The clean payload.
    """
    daemonData = baker.prepare(
        DaemonModel,
        mailbox=mailboxModel,
        fetching_criterion=random.choice(mailboxModel.getAvailableFetchingCriteria()),
        cycle_interval=random.randint(
            DaemonModel.cycle_interval.field.default + 1,
            DaemonModel.cycle_interval.field.default * 100,
        ),
        restart_time=random.randint(
            DaemonModel.restart_time.field.default + 1,
            DaemonModel.restart_time.field.default * 100,
        ),
        log_backup_count=random.randint(
            DaemonModel.log_backup_count.field.default + 1,
            DaemonModel.log_backup_count.field.default * 100,
        ),
        logfile_size=random.randint(
            DaemonModel.logfile_size.field.default + 1,
            DaemonModel.logfile_size.field.default * 100,
        ),
        log_filepath=faker.file_path(),
    )
    payload = model_to_dict(daemonData)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.fixture
def emailPayload(faker, mailboxModel) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.EMailModel.EMailModel` payload with data deviating from the defaults.

    Args:
        mailboxModel: Depends on :func:`mailboxModel`.

    Returns:
        The clean payload.
    """
    emailData = baker.prepare(
        EMailModel,
        mailbox=mailboxModel,
        email_subject=faker.sentence(),
        plain_bodytext=faker.text(),
        html_bodytext=faker.text(),
        is_favorite=not EMailModel.is_favorite.field.default,
        x_spam="NO",
    )
    payload = model_to_dict(emailData)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.fixture
def mailboxPayload(accountModel) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.MailboxModel.MailboxModel` payload with data deviating from the defaults.

    Args:
        accountModel: Depends on :func:`accountModel`.

    Returns:
        The clean payload.
    """
    mailboxData = baker.prepare(
        MailboxModel,
        account=accountModel,
        save_attachments=not MailboxModel.save_attachments.field.default,
        save_toEML=not MailboxModel.save_toEML.field.default,
        is_favorite=not MailboxModel.is_favorite.field.default,
    )
    payload = model_to_dict(mailboxData)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.fixture
def mailingListPayload(faker, emailModel) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.MailingListModel.MailingListModel` payload with data deviating from the defaults.

    Args:
        emailModel: Depends on :func:`emailModel`.

    Returns:
        The clean payload.
    """
    mailinglistData = baker.prepare(
        MailingListModel,
        emails=[emailModel],
        list_owner=faker.name(),
        list_subscribe=faker.email(),
        list_unsubscribe=faker.email(),
        list_post=faker.email(),
        list_archive=faker.url(),
        list_help=faker.url(),
        is_favorite=not MailingListModel.is_favorite.field.default,
    )
    payload = model_to_dict(mailinglistData)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}
