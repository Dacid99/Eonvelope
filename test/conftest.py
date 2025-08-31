# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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

"""File with fixtures and configurations required for all tests. Automatically imported to `test_` files.

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

    block with
    cleanup
"""

from __future__ import annotations

import contextlib
import os
from datetime import UTC, datetime, timedelta, timezone
from io import BytesIO
from tempfile import gettempdir
from typing import TYPE_CHECKING

import pytest
from django.core.files.storage import default_storage
from django.forms import model_to_dict
from django_celery_beat.models import IntervalSchedule
from model_bakery import baker
from pyfakefs.fake_filesystem_unittest import Patcher, Pause

from core.constants import (
    EmailProtocolChoices,
    HeaderFields,
)
from core.models import (
    Account,
    Attachment,
    Correspondent,
    Daemon,
    Email,
    EmailCorrespondent,
    Mailbox,
)
from Emailkasten.middleware.TimezoneMiddleware import TimezoneMiddleware


if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Any

    from django.contrib.auth.models import AbstractUser
    from pyfakefs.fake_filesystem import FakeFilesystem


def pytest_configure(config) -> None:
    """Configures the path for pytest to be the directory of this file for consistent relative paths."""
    pytest_ini_dir = os.path.dirname(os.path.abspath(config.inifile))
    os.chdir(pytest_ini_dir)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test.settings")


# test_email_path, expected_email_features, expected_correspondents_features, expected_attachments_features
TEST_EMAIL_PARAMETERS = [
    (
        "test_emails/attachmentjson.eml",
        {
            "message_id": "<e047e14d-2397-435b-baf6-8e8b7423f860@bvncmx.com>",
            "email_subject": "What's up",
            "date": datetime(
                2024, 8, 7, 11, 41, 29, tzinfo=timezone(timedelta(seconds=7200))
            ),
            "x_spam": "NO",
            "plain_bodytext": "this a test to see how ur doing\r\n\r\n\r\n\r\n\r\n",
            "html_bodytext": "",
            "references": [],
            "header_count": 20,
        },
        {
            "return-path": {
                "mnbvcfg.48ij343regrh8ge5jp02b@bvncmx.com": {"name": ""},
            },
            "from": {
                "mnbvcfg.48ij343regrh8ge5jp02b@bvncmx.com": {
                    "name": "xsejino mnkfsdfuio"
                },
            },
            "envelope-to": {
                "test@48ij343regrh8ge5jp02b.org": {"name": ""},
            },
            "to": {
                "test@48ij343regrh8ge5jp02b.org": {"name": ""},
            },
            "cc": {
                "sndfbkl48ij343regrh8ge5jp02b@bvncmx.com": {"name": ""},
            },
        },
        {
            "manifest.json": {
                "content_maintype": "application",
                "content_subtype": "json",
                "content_disposition": "attachment",
                "content_id": "",
            }
        },
    ),
    (
        "test_emails/inlineimage.eml",
        {
            "message_id": "<a634b121-4bc0-457d-a08f-a4579b9bb92a@bvncmx.com>",
            "email_subject": "more image",
            "date": datetime(
                2024, 10, 5, 14, 43, 21, tzinfo=timezone(timedelta(seconds=7200))
            ),
            "x_spam": "NO",
            "plain_bodytext": "\r\ntry this\r\n",
            "html_bodytext": '<!DOCTYPE html>\r\n<html>\r\n  <head>\r\n\r\n    <meta http-equiv="content-type" content="text/html; charset=UTF-8">\r\n  </head>\r\n  <body>\r\n    <p><img src="cid:part1.DePPID0S.dKVK0mlg@bvncmx.com" alt=""></p>\r\n    <p><br>\r\n    </p>\r\n    <p>try this<br>\r\n    </p>\r\n  </body>\r\n</html>',
            "references": [],
            "header_count": 21,
        },
        {
            "return-path": {
                "sndfbkl48ij343regrh8ge5jp02b@bvncmx.com": {"name": ""},
            },
            "from": {
                "sndfbkl48ij343regrh8ge5jp02b@bvncmx.com": {"name": "QNfjq"},
            },
            "envelope-to": {
                "test@48ij343regrh8ge5jp02b.org": {"name": ""},
            },
            "to": {
                "test@48ij343regrh8ge5jp02b.org": {"name": ""},
            },
        },
        {
            "Z4md6xHlrYcKHhKK.png": {
                "content_maintype": "image",
                "content_subtype": "png",
                "content_disposition": "inline",
                "content_id": "<part1.DePPID0S.dKVK0mlg@bvncmx.com>",
            }
        },
    ),
    (
        "test_emails/textplain.eml",
        {
            "message_id": "<622b772d-0839-4ff3-9f31-2313b0b57040@bvncmx.com>",
            "email_subject": "Testmail",
            "date": datetime(
                2024, 8, 1, 15, 35, 52, tzinfo=timezone(timedelta(seconds=7200))
            ),
            "x_spam": "NO",
            "plain_bodytext": "Hi\r\n\r\nThis is a test!\r\n\r\näöü\r\n\r\nViele Grüße,\r\n\r\nQNfjq\r\n",
            "html_bodytext": "",
            "references": [],
            "header_count": 22,
        },
        {
            "return-path": {
                "sndfbkl48ij343regrh8ge5jp02b@bvncmx.com": {"name": ""},
            },
            "from": {
                "sndfbkl48ij343regrh8ge5jp02b@bvncmx.com": {"name": "QNfjq"},
            },
            "envelope-to": {
                "test@48ij343regrh8ge5jp02b.org": {"name": ""},
            },
            "to": {
                "test@48ij343regrh8ge5jp02b.org": {"name": ""},
            },
        },
        {},
    ),
    (
        "test_emails/multipartalternative_basic.eml",
        {
            "message_id": "<320b8a44-3d8c-457d-b590-0d33290ae599@prov.de>",
            "email_subject": "Welcome back",
            "date": datetime(2024, 8, 9, 16, 20, 23, tzinfo=UTC),
            "x_spam": "NO",
            "plain_bodytext": "\r\n\r\nSehr geehrte ,\r\n\r\n\r\n\r\nViele Grüße,\r\nDavid\r\n",
            "html_bodytext": '<html>\r\n<head>\r\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\r\n</head>\r\n<body>\r\n<div dir="auto"><br>\r\n<br>\r\n</div>\r\n<div dir="auto"><!-- tmjah_g_1299s -->Sehr geehrte ,<!-- tmjah_g_1299e --><br>\r\n<br>\r\n<br>\r\n<br>\r\n</div>\r\n<div dir="auto"><!-- tmjah_g_1299s -->Viele Grüße,<!-- tmjah_g_1299e --><br>\r\n</div>\r\n<div dir="auto"><!-- tmjah_g_1299s -->David<!-- tmjah_g_1299e --></div>\r\n</body>\r\n</html>\r\n',
            "references": [],
            "header_count": 21,
        },
        {
            "return-path": {
                "prvs=1951f1b812=48ij343regrh8ge5jp02b@uttgjub8.de": {"name": ""},
            },
            "from": {
                "48ij343regrh8ge5jp02b@uttgjub8.de": {"name": "mnkfsdfuio, QNfjq"},
            },
            "envelope-to": {
                "test@48ij343regrh8ge5jp02b.org": {"name": ""},
            },
            "to": {
                "test@48ij343regrh8ge5jp02b.org": {
                    "name": "test@48ij343regrh8ge5jp02b.org"
                },
            },
        },
        {},
    ),
    (
        "test_emails/doubleCC.eml",
        {
            "message_id": "<CACjuskUOYbprYYU9-L3CrZ5RjNHdo9c9A4z7pFDC=8JKheDWSQ@mail.bvncmx.com>",
            "email_subject": "Test for cc header",
            "date": datetime(
                2024, 10, 18, 17, 11, 50, tzinfo=timezone(timedelta(seconds=7200))
            ),
            "x_spam": "NO",
            "plain_bodytext": "another test for the correspondents ..\r\n",
            "html_bodytext": '<div dir="ltr">another test for the correspondents ..<br></div>\r\n',
            "references": [],
            "header_count": 19,
        },
        {
            "return-path": {
                "sndfbkl48ij343regrh8ge5jp02b@bvncmx.com": {"name": ""},
            },
            "from": {
                "sndfbkl48ij343regrh8ge5jp02b@bvncmx.com": {"name": "Hungry Burger"},
            },
            "envelope-to": {
                "test@48ij343regrh8ge5jp02b.org": {"name": ""},
            },
            "to": {
                "test@48ij343regrh8ge5jp02b.org": {"name": ""},
            },
            "cc": {
                "wehrnfg@48ij343regrh8ge5jp02b.org": {"name": "QNfjq"},
                "wehrnfg.48ij343regrh8ge5jp02b@picge1.de": {"name": ""},
            },
        },
        {},
    ),
    (
        "test_emails/message_id_spelling.eml",
        {
            "message_id": "<20250701174450.26ae316c8d2af4a9@notify.docker.com>",
            "email_subject": "[Docker] A personal access token was created",
            "date": datetime(
                2025, 7, 1, 17, 44, 50, tzinfo=timezone(timedelta(seconds=0))
            ),
            "x_spam": "NO",
            "plain_bodytext": "Hello user!\n\n\nA personal access token was just created now for the Docker account user.\nAccess token description: test\n\nThis access token will now function as a password for the Docker CLI. If you created this personal access token, no more action is required. If you did not create this access token, please go to Personal Access Tokens Settings at <no value>. Delete the token, then change your password.\n\nThank you,\nThe Docker Team\n\nThis email was sent to your mail to notify you of an update that was made to your Docker Account.\n\n© 2025 Docker Inc.\n3790 El Camino Real #1052, Palo Alto, CA 94306\n",
            "html_bodytext": "",
            "references": [],
            "header_count": 17,
        },
        {
            "return-path": {
                "bounce+670d3d.5e6ef-your=mail.org@notify.docker.com": {"name": ""},
            },
            "sender": {
                "no-reply@notify.docker.com": {"name": ""},
            },
            "from": {
                "no-reply@notify.docker.com": {"name": "Docker"},
            },
            "envelope-to": {
                "your@mail.org": {"name": ""},
            },
            "to": {
                "your@mail.org": {"name": ""},
            },
        },
        {},
    ),
]


@pytest.fixture
def fake_file_bytes(faker) -> bytes:
    """Random bytes to act as file content."""
    return faker.text().encode()


@pytest.fixture
def fake_file(fake_file_bytes) -> BytesIO:
    """A filestream with random content."""
    return BytesIO(fake_file_bytes)


@pytest.fixture
def fake_timezone(faker):
    """A random timezone."""
    return faker.timezone()


@pytest.fixture
def fake_timezone_client(client, fake_timezone):
    """A client with session timezone from :func:`fake_timezone`."""
    session = client.session
    session[TimezoneMiddleware.TIMEZONE_SESSION_KEY] = fake_timezone
    session.save()
    return client


@pytest.fixture
def fake_bad_timezone_client(client):
    """A client with invalid session timezone."""
    session = client.session
    session[TimezoneMiddleware.TIMEZONE_SESSION_KEY] = "NO/TZONE"
    session.save()


@pytest.fixture
def fake_fs(settings) -> Generator[FakeFilesystem]:
    """A mock Linux filesystem for realistic testing.

    Contains a directory at the STORAGE_PATH setting to allow for testing without patching the storage backend.
    Contains a directory at the LOG_DIRECTORY_PATH setting.
    Contains a tempdir at the location requested by tempfile.
    """
    with Patcher() as patcher:
        if not patcher.fs:
            raise OSError("Generator could not create a fakefs!")

        patcher.fs.create_dir(settings.STORAGE_PATH)
        patcher.fs.create_dir(settings.LOG_DIRECTORY_PATH)
        with contextlib.suppress(OSError):
            patcher.fs.create_dir(gettempdir())

        yield patcher.fs


@pytest.fixture
def owner_user(django_user_model) -> AbstractUser:
    """A user that owns the data."""
    return baker.make(django_user_model)


@pytest.fixture
def other_user(django_user_model) -> AbstractUser:
    """A user that is not the owner of the data."""
    return baker.make(django_user_model)


@pytest.fixture
def fake_account(owner_user) -> Account:
    """An :class:`core.models.Account` owned by :attr:`owner_user`.

    Note:
        The protocol is always IMAP to allow for different fetchingoptions.
    """
    return baker.make(
        Account, user=owner_user, protocol=EmailProtocolChoices.IMAP.value
    )


@pytest.fixture
def fake_mailbox(fake_account) -> Mailbox:
    """An :class:`core.models.Mailbox` owned by :attr:`owner_user`."""
    return baker.make(Mailbox, account=fake_account)


@pytest.fixture
def fake_daemon(fake_mailbox) -> Daemon:
    """An :class:`core.models.Daemon` owned by :attr:`owner_user`."""
    return baker.make(
        Daemon,
        mailbox=fake_mailbox,
    )


@pytest.fixture
def fake_email(fake_mailbox) -> Email:
    """An :class:`core.models.Email` owned by :attr:`owner_user`."""
    return baker.make(Email, mailbox=fake_mailbox)


@pytest.fixture
def fake_correspondent(fake_email) -> Correspondent:
    """An :class:`core.models.Correspondent` owned by :attr:`owner_user`."""
    return baker.make(Correspondent, user=fake_email.mailbox.account.user)


@pytest.fixture
def fake_email_with_file(faker, fake_fs, fake_mailbox) -> Email:
    """An :class:`core.models.Email` owned by :attr:`owner_user`."""
    with Pause(fake_fs), open(TEST_EMAIL_PARAMETERS[0][0], "rb") as test_email:
        test_eml_bytes = test_email.read()
    return baker.make(
        Email,
        mailbox=fake_mailbox,
        eml_filepath=default_storage.save(
            faker.file_name(extension="eml"), BytesIO(test_eml_bytes)
        ),
    )


@pytest.fixture
def fake_email_conversation(fake_email):
    """Fixture creating a conversation around `fake_email`."""
    reply_mails = baker.make(Email, mailbox=fake_email.mailbox, _quantity=3)
    for email in reply_mails:
        email.in_reply_to.add(fake_email)
        email.references.add(fake_email)
    for email in baker.make(Email, _quantity=2, mailbox=fake_email.mailbox):
        email.in_reply_to.add(reply_mails[1])
        email.references.add(reply_mails[1])
        email.references.add(fake_email)
    reply_reply_mail = baker.make(Email, mailbox=fake_email.mailbox)
    reply_reply_mail.in_reply_to.add(reply_mails[0])
    reply_reply_mail.references.add(reply_mails[0])
    reply_reply_mail.references.add(fake_email)
    reply_reply_reply_mail = baker.make(Email, mailbox=fake_email.mailbox)
    reply_reply_reply_mail.in_reply_to.add(reply_reply_mail)
    reply_reply_reply_mail.references.add(reply_reply_mail)
    reply_reply_reply_mail.references.add(reply_mails[0])
    reply_reply_reply_mail.references.add(fake_email)


@pytest.fixture
def fake_emailcorrespondent(fake_correspondent, fake_email) -> EmailCorrespondent:
    """Fixture creating an :class:`core.models.EmailCorrespondent`."""
    return baker.make(
        EmailCorrespondent,
        email=fake_email,
        correspondent=fake_correspondent,
        mention=HeaderFields.Correspondents.FROM,
    )


@pytest.fixture
def fake_attachment(faker, fake_email) -> Attachment:
    """An :class:`core.models.Attachment` owned by :attr:`owner_user`."""
    return baker.make(
        Attachment,
        email=fake_email,
        content_maintype=faker.word(),
        content_subtype=faker.word(),
    )


@pytest.fixture
def fake_attachment_with_file(faker, fake_file, fake_fs, fake_email) -> Attachment:
    """An :class:`core.models.Attachment` owned by :attr:`owner_user`."""
    return baker.make(
        Attachment,
        email=fake_email,
        file_path=default_storage.save(faker.file_name(), fake_file),
    )


@pytest.fixture
def fake_other_account(other_user) -> Account:
    """An :class:`core.models.Account` owned by :attr:`other_user`.

    Note:
        The protocol is always IMAP to allow for different fetchingoptions.

    """
    return baker.make(
        Account, user=other_user, protocol=EmailProtocolChoices.IMAP.value
    )


@pytest.fixture
def fake_other_mailbox(fake_other_account) -> Mailbox:
    """An :class:`core.models.Mailbox` owned by :attr:`other_user`."""
    return baker.make(Mailbox, account=fake_other_account)


@pytest.fixture
def fake_other_daemon(faker, fake_other_mailbox) -> Daemon:
    """An :class:`core.models.Daemon` owned by :attr:`other_user`."""
    return baker.make(
        Daemon,
        mailbox=fake_other_mailbox,
    )


@pytest.fixture
def fake_other_email(faker, fake_other_mailbox) -> Email:
    """An :class:`core.models.Email` owned by :attr:`other_user`."""
    return baker.make(Email, mailbox=fake_other_mailbox)


@pytest.fixture
def fake_other_correspondent(fake_other_email) -> Correspondent:
    """An :class:`core.models.Correspondent` owned by :attr:`other_user`."""
    return baker.make(Correspondent, user=fake_other_email.mailbox.account.user)


@pytest.fixture
def fake_other_email_with_file(faker, fake_fs, fake_other_mailbox) -> Email:
    """An :class:`core.models.Email` owned by :attr:`other_user`."""
    with Pause(fake_fs), open(TEST_EMAIL_PARAMETERS[0][0], "rb") as test_email:
        test_eml_bytes = test_email.read()
    return baker.make(
        Email,
        mailbox=fake_other_mailbox,
        eml_filepath=default_storage.save(
            faker.file_name(extension="eml"), BytesIO(test_eml_bytes)
        ),
    )


@pytest.fixture
def fake_other_emailcorrespondent(
    fake_other_correspondent, fake_other_email
) -> EmailCorrespondent:
    """Fixture creating an :class:`core.models.EmailCorrespondent`."""
    return baker.make(
        EmailCorrespondent,
        email=fake_other_email,
        correspondent=fake_other_correspondent,
        mention=HeaderFields.Correspondents.FROM,
    )


@pytest.fixture
def fake_other_attachment(fake_other_email) -> Attachment:
    """An :class:`core.models.Attachment` owned by :attr:`other_user`."""
    return baker.make(Attachment, email=fake_other_email)


@pytest.fixture
def fake_other_attachment_with_file(
    faker, fake_file, fake_fs, fake_other_email
) -> Attachment:
    """An :class:`core.models.Attachment` owned by :attr:`other_user`."""
    return baker.make(
        Attachment,
        email=fake_other_email,
        file_path=default_storage.save(faker.file_name(), fake_file),
    )


@pytest.fixture
def account_payload(faker, owner_user) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.Account` payload with data deviating from the defaults."""
    account_data = baker.prepare(
        Account,
        user=owner_user,
        mail_host_port=faker.random.randint(0, 65535),
        protocol=faker.random.choice(EmailProtocolChoices.values),
        timeout=faker.random.randint(1, 1000),
        is_favorite=not Account.is_favorite.field.default,
    )
    payload = model_to_dict(account_data)
    payload.pop("id")
    payload.pop("user")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.fixture
def attachment_payload(faker, fake_email) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.Attachment` payload with data deviating from the defaults."""
    attachment_data = baker.prepare(
        Attachment,
        email=fake_email,
        content_disposition=faker.name(),
        content_id=faker.name(),
        content_maintype=faker.name(),
        content_subtype=faker.name(),
        is_favorite=not Attachment.is_favorite.field.default,
    )
    payload = model_to_dict(attachment_data)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.fixture
def correspondent_payload(faker, fake_email) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.Correspondent` payload with data deviating from the defaults."""
    correspondent_data = baker.prepare(
        Correspondent,
        emails=[fake_email],
        real_name=faker.name(),
        email_name=faker.name(),
        list_id=faker.name(),
        list_owner=faker.name(),
        list_subscribe=faker.email(),
        list_unsubscribe=faker.email(),
        list_post=faker.email(),
        list_archive=faker.url(),
        list_help=faker.url(),
        is_favorite=not Correspondent.is_favorite.field.default,
    )
    payload = model_to_dict(correspondent_data)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.fixture
def daemon_payload(faker, fake_mailbox, fake_daemon) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.Daemon` payload with data deviating from the defaults."""
    # no cryptography going on here
    fetching_choices = list(fake_mailbox.available_fetching_criteria)
    if fake_daemon.fetching_criterion in fetching_choices:
        fetching_choices.remove(fake_daemon.fetching_criterion)
    daemon_data = baker.prepare(
        Daemon,
        mailbox=fake_mailbox,
        fetching_criterion=faker.random.choice(fetching_choices),
    )
    payload = model_to_dict(daemon_data)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.fixture
def daemon_with_interval_payload(daemon_payload):
    """Payload for a daemon form."""
    interval = baker.prepare(IntervalSchedule)
    daemon_payload["interval_every"] = abs(interval.every)
    daemon_payload["interval_period"] = interval.period
    return daemon_payload


@pytest.fixture
def email_payload(faker, fake_mailbox) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.Email` payload with data deviating from the defaults."""
    email_data = baker.prepare(
        Email,
        mailbox=fake_mailbox,
        email_subject=faker.sentence(),
        plain_bodytext=faker.text(),
        html_bodytext=faker.text(),
        is_favorite=not Email.is_favorite.field.default,
        x_spam="NO",
    )
    payload = model_to_dict(email_data)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.fixture
def mailbox_payload(fake_account) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.Mailbox` payload with data deviating from the defaults."""
    mailbox_data = baker.prepare(
        Mailbox,
        account=fake_account,
        save_attachments=not Mailbox.save_attachments.field.default,
        save_to_eml=not Mailbox.save_to_eml.field.default,
        is_favorite=not Mailbox.is_favorite.field.default,
    )
    payload = model_to_dict(mailbox_data)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}
