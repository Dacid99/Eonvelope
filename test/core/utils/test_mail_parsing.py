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

"""Test module for :mod:`core.utils.mail_parsing`."""

import email
from datetime import datetime
from email import policy
from email.message import EmailMessage
from email.utils import format_datetime

import pytest

from core.utils import mail_parsing
from test.conftest import TEST_EMAIL_PARAMETERS


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """The mocked :attr:`core.utils.mail_parsing.logger`."""
    return mocker.patch("core.utils.mail_parsing.logger", autospec=True)


@pytest.fixture
def fake_single_header(faker):
    """Fixture providing a header tuple with a single value."""
    return (faker.word(), faker.sentence(nb_words=5))


@pytest.fixture
def fake_date_headervalue(faker):
    """Fixture providing a datetime value."""
    return faker.date_time(tzinfo=faker.pytimezone())


@pytest.fixture
def fake_unstripped_header(faker):
    """Fixture providing a header tuple with an unstripped value."""
    return (faker.word(), " " + faker.sentence(nb_words=2) + "  ")


@pytest.fixture
def fake_multi_header(faker):
    """Fixture providing a header tuple with multiple values."""
    return (
        faker.word(),
        [faker.sentence(nb_words=5), faker.name(), "  " + faker.name() + " "],
    )


@pytest.fixture
def email_message(fake_single_header, fake_unstripped_header, fake_multi_header):
    """Fixture providing a valid :class:`email.message.EmailMessage` with various headers."""
    test_message = EmailMessage()
    test_message.add_header(*fake_single_header)
    test_message.add_header(*fake_unstripped_header)
    for value in fake_multi_header[1]:
        test_message.add_header(fake_multi_header[0], value)
    return test_message


@pytest.fixture
def bad_email_message():
    """Fixture providing an :class:`email.message.EmailMessage` with an invalid header."""
    test_message = EmailMessage()
    test_message.add_header("Date", "not a datetime str")
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
    """Tests :func:`core.utils.mail_parsing.decode_header`."""
    result = mail_parsing.decode_header(header)

    assert result == expected_result


def test_get_header_single_success(email_message, fake_single_header):
    """Tests :func:`core.utils.mail_parsing.get_header`
    in case the header exists once.
    """
    result = mail_parsing.get_header(email_message, fake_single_header[0])

    assert result == fake_single_header[1].strip()


def test_get_header_unstripped_success(email_message, fake_unstripped_header):
    """Tests :func:`core.utils.mail_parsing.get_header`
    in case the header is unstripped.
    """
    result = mail_parsing.get_header(email_message, fake_unstripped_header[0])

    assert result == fake_unstripped_header[1].strip()


def test_get_header_multi_success(email_message, fake_multi_header):
    """Tests :func:`core.utils.mail_parsing.get_header`
    in case the header exists multiple times.
    """
    result = mail_parsing.get_header(email_message, fake_multi_header[0])

    assert result == ",".join([header.strip() for header in fake_multi_header[1]])


def test_get_header_multi_joinparam_success(email_message, fake_multi_header):
    """Tests :func:`core.utils.mail_parsing.get_header`
    in case the header exists multiple times and a joining_string is given.
    """
    result = mail_parsing.get_header(
        email_message, fake_multi_header[0], joining_string="test"
    )

    assert result == "test".join([header.strip() for header in fake_multi_header[1]])


def test_get_header_fallback(fake_single_header):
    """Tests :func:`core.utils.mail_parsing.get_header`
    in case the header doesn't exists.
    """
    result = mail_parsing.get_header(EmailMessage(), fake_single_header[0])

    assert result == ""


def test_get_header_failure(fake_single_header):
    """Tests :func:`core.utils.mail_parsing.get_header`
    in case there is no emailmessage.
    """
    with pytest.raises(AttributeError):
        mail_parsing.get_header(None, fake_single_header[0])


def test_parse_datetime_header_success(faker, mock_logger):
    """Tests :func:`core.utils.mail_parsing.parse_datetime_header`
    in case of success.
    """
    fake_date_headervalue = format_datetime(faker.date_time(tzinfo=faker.pytimezone()))

    result = mail_parsing.parse_datetime_header(fake_date_headervalue)

    mock_logger.warning.assert_not_called()
    assert isinstance(result, datetime)
    assert format_datetime(result) == fake_date_headervalue


def test_parse_datetime_header_fallback(mocker, faker, mock_logger):
    """Tests :func:`core.utils.mail_parsing.parse_datetime_header`
    in case the datetime header can't be parsed.
    """
    mock_timezone_now = mocker.patch(
        "django.utils.timezone.now", autospec=True, return_value=faker.date_time()
    )

    result = mail_parsing.parse_datetime_header("no datetime header")

    mock_logger.warning.assert_called()
    mock_timezone_now.assert_called()
    assert isinstance(result, datetime)
    assert format_datetime(result) == format_datetime(mock_timezone_now.return_value)


def test_parse_datetime_header_no_header(mocker, faker, mock_logger):
    """Tests :func:`core.utils.mail_parsing.parse_datetime_header`
    in case there is no header.
    """
    mock_timezone_now = mocker.patch(
        "django.utils.timezone.now", autospec=True, return_value=faker.date_time()
    )

    result = mail_parsing.parse_datetime_header(None)

    mock_logger.warning.assert_called()
    mock_timezone_now.assert_called()
    assert isinstance(result, datetime)
    assert format_datetime(result) == format_datetime(mock_timezone_now.return_value)


@pytest.mark.parametrize(
    "name_data, expected_name",
    [
        (b"INBOX", "INBOX"),
        ("INBOX", "INBOX"),
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
            '(\\Sent \\HasNoChildren) "/" "Gesendete Objekte"',
            '"Gesendete Objekte"',
        ),
        (
            b'(\\Sent \\HasChildren) "." INBOX.Sent',
            "INBOX.Sent",
        ),
        (
            b'(\\HasNoChildren) "/" Archive/2024',
            "Archive/2024",
        ),
        (
            b'() ";" Trash',
            "Trash",
        ),
    ],
)
def test_parse_mailbox_name(name_data, expected_name):
    """Tests :func:`core.utils.mail_parsing.parse_mailbox_name`."""
    result = mail_parsing.parse_mailbox_name(name_data)

    assert result == expected_name


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
    """Tests :func:`core.utils.mail_parsing.get_bodytexts` on test-email data."""
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
    "header, expected_href",
    [
        ("", ""),
        ("https://test.list.com", "https://test.list.com"),
        ("<https://usub.maillist.io>", "https://usub.maillist.io"),
        ("<mailto:getridofthe@list.us>, <http://other.way.us>,", "http://other.way.us"),
        ("<mailto:one@mail.it>, <mailto:other@mail.it>,", "mailto:one@mail.it"),
        ("<https://firstref.ca>, https://secondref.ca,", "https://firstref.ca"),
        ("http://insecure.ru, https://sslftw.org,", "https://sslftw.org"),
    ],
)
def test_find_best_href_in_header(header, expected_href):
    """Tests :func:`core.utils.mail_parsing.find_best_href_in_header`
    for different typical cases of header.
    """
    result = mail_parsing.find_best_href_in_header(header)

    assert result == expected_href


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
