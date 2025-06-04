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

"""Test module for :mod:`core.utils.mail_parsing`."""

import email
from datetime import datetime
from email import policy
from email.message import EmailMessage
from email.utils import format_datetime

import pytest

from core.utils import mail_parsing

from ...conftest import TEST_EMAIL_PARAMETERS


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Mocks :attr:`logger` of the module."""
    return mocker.patch("core.utils.mail_parsing.logger", autospec=True)


@pytest.fixture
def fake_single_header(faker):
    return (faker.word(), faker.sentence(nb_words=5))


@pytest.fixture
def fake_date_headervalue(faker):
    return faker.date_time(tzinfo=faker.pytimezone())


@pytest.fixture
def fake_multi_header(faker):
    return (faker.word(), [faker.sentence(nb_words=5), faker.name(), faker.file_name()])


@pytest.fixture
def email_message(fake_single_header, fake_multi_header):
    """A valid :class:`email.message.EmailMessage`."""
    test_message = EmailMessage()
    test_message.add_header(*fake_single_header)
    for value in fake_multi_header[1]:
        test_message.add_header(fake_multi_header[0], value)
    return test_message


@pytest.fixture
def bad_email_message():
    """A valid :class:`email.message.EmailMessage`."""
    test_message = EmailMessage()
    test_message.add_header("Date", "not a datetime str")
    return test_message


@pytest.fixture
def empty_email_message():
    """An invalid :class:`email.message.Message`."""
    test_message = EmailMessage()
    return test_message


@pytest.fixture
def no_email_message():
    """A none message."""
    test_message = None
    return test_message


@pytest.mark.parametrize(
    "header, expected_result",
    [
        (
            "Some header text without special chars",
            "Some header text without special chars",
        ),
        (
            "=?utf-8?q?H=C3=A4ng=C3=B1en_Loch_Junge_also_m=C3=BCssen=C3=A1?= Wetter.",
            "Hängñen Loch Junge also müssená Wetter.",
        ),
        (
            "Ms. Cassandra =?utf-8?b?R2lsbGVz0JRwafCfmIpl?= <aliciaward@example.com>",
            "Ms. Cassandra GillesДpi😊e <aliciaward@example.com>",
        ),
        (
            "=?utf-8?q?=C3=89tabl=C3=A9ir_mur_souffler_casser=C3=AD?= comprendre.",
            "Établéir mur souffler casserí comprendre.",
        ),
        (
            "=?utf-8?b?5Lit5bO24piF0Jkg6Zm95a2Q?= <kenichiito@example.com>",
            "中島★Й 陽子 <kenichiito@example.com>",
        ),
    ],
)
def test_decode_header_success(header, expected_result):
    result = mail_parsing.decode_header(header)

    assert result == expected_result


def test_get_header_single_success(email_message, fake_single_header):
    result = mail_parsing.get_header(email_message, fake_single_header[0])

    assert result == fake_single_header[1]


def test_get_header_multi_success(email_message, fake_multi_header):
    result = mail_parsing.get_header(email_message, fake_multi_header[0])

    assert result == ", ".join(fake_multi_header[1])


def test_get_header_multi_joinparam_success(email_message, fake_multi_header):
    result = mail_parsing.get_header(
        email_message, fake_multi_header[0], joining_string="test"
    )

    assert result == "test".join(fake_multi_header[1])


def test_get_header_fallback(empty_email_message, fake_single_header):
    result = mail_parsing.get_header(empty_email_message, fake_single_header[0])

    assert result == ""


def test_get_header_failure(no_email_message, fake_single_header):
    with pytest.raises(AttributeError):
        mail_parsing.get_header(no_email_message, fake_single_header[0])


def test_parse_datetime_header_success(faker, mock_logger):
    fake_date_headervalue = format_datetime(faker.date_time(tzinfo=faker.pytimezone()))

    result = mail_parsing.parse_datetime_header(fake_date_headervalue)

    mock_logger.warning.assert_not_called()
    assert isinstance(result, datetime)
    assert format_datetime(result) == fake_date_headervalue


def test_parse_datetime_header_fallback(mocker, faker, mock_logger):
    mock_timezone_now = mocker.patch(
        "django.utils.timezone.now", autospec=True, return_value=faker.date_time()
    )

    result = mail_parsing.parse_datetime_header("no datetime header")

    mock_logger.warning.assert_called()
    mock_timezone_now.assert_called()
    assert isinstance(result, datetime)
    assert format_datetime(result) == format_datetime(mock_timezone_now.return_value)


def test_parse_datetime_header_no_header(mocker, faker, mock_logger):
    mock_timezone_now = mocker.patch(
        "django.utils.timezone.now", autospec=True, return_value=faker.date_time()
    )

    result = mail_parsing.parse_datetime_header(None)

    mock_logger.warning.assert_called()
    mock_timezone_now.assert_called()
    assert isinstance(result, datetime)
    assert format_datetime(result) == format_datetime(mock_timezone_now.return_value)


@pytest.mark.parametrize(
    "name_bytes, expected_name",
    [
        (b"INBOX", "INBOX"),
        (
            b'Dr&AOc-. Bianka "/" F&APY-rste&BBk-r',
            "FörsteЙr",
        ),
        (
            b'Yves "/" Pr&AN8EGQ-uvost',
            "PrßЙuvost",
        ),
        (
            b'&ZY4mBQDfheQ- "/" &Zg5,jg-',
            "明美",
        ),
        (
            b'(\\Sent \\HasNoChildren) "/" "Gesendete Objekte"',
            '"Gesendete Objekte"',
        ),
        (
            b'(\\HasNoChildren) "/" Archive/2024',
            "Archive/2024",
        ),
    ],
)
def test_parse_mailbox_name_success(name_bytes, expected_name):
    result = mail_parsing.parse_mailbox_name(name_bytes)

    assert result == expected_name


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_email_path, expected_email_features, expected_correspondents_features,expected_attachments_features",
    TEST_EMAIL_PARAMETERS,
)
def test_message2html(
    test_email_path,
    expected_email_features,
    expected_correspondents_features,
    expected_attachments_features,
):
    with open(test_email_path, "br") as test_email_file:
        test_email_bytes = test_email_file.read()

    result = mail_parsing.message2html(
        email.message_from_bytes(test_email_bytes, policy=policy.default)
    )

    assert result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_email_path, expected_email_features, expected_correspondents_features,expected_attachments_features",
    TEST_EMAIL_PARAMETERS,
)
def test_get_bodytexts(
    test_email_path,
    expected_email_features,
    expected_correspondents_features,
    expected_attachments_features,
):
    with open(test_email_path, "br") as test_email_file:
        test_email_message = email.message_from_bytes(
            test_email_file.read(), policy=policy.default
        )

    result = mail_parsing.get_bodytexts(test_email_message)

    assert ("plain" in result) is bool(expected_email_features["plain_bodytext"])
    assert result.get("plain", "") == expected_email_features["plain_bodytext"]
    assert ("html" in result) is bool(expected_email_features["html_bodytext"])
    assert result.get("html", "") == expected_email_features["html_bodytext"]


@pytest.mark.parametrize(
    "x_spam, expected_result",
    [
        (None, False),
        ("", False),
        ("YES", True),
        ("NO", False),
        ("NO, YES", True),
        ("YES, YES", True),
        ("NO, NO", False),
        ("CRAZY", False),
    ],
)
def test_is_x_spam(x_spam, expected_result):
    """Tests :func:`core.models.Email.Email.is_spam`."""
    result = mail_parsing.is_x_spam(x_spam)

    assert result is expected_result
