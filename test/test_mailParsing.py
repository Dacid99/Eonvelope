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

"""Test module for :mod:`core.utils.mailParsing`.

Fixtures:
    :func:`fixture_mock_logger`: Mocks :attr:`logger` of the module.
    :func:`fixture_mock_good_mailMessage`: Mocks a valid :class:`email.message.Message`.
    :func:`fixture_mock_special_mailMessage`: Mocks a valid :class:`email.message.Message` with special contents.
    :func:`fixture_mock_bad_mailMessage`: Mocks an invalid :class:`email.message.Message`.
    :func:`fixture_mock_no_mailMessage`: Mocks a none message.
    :func:`fixture_mock_empty_parsedMailDict`: Mocks an empty parsedMail :class:`dict` that the mail is parsed into.
"""

import datetime
from email.message import Message

import pytest

import core.constants
import core.utils.mailParsing


@pytest.fixture(name="mock_logger", autouse=True)
def fixture_mock_logger(mocker):
    """Mocks :attr:`logger` of the module."""
    return mocker.patch("core.utils.mailParsing.logger")


@pytest.fixture(name="mock_good_mailMessage", scope="module")
def fixture_mock_good_mailMessage():
    """Mocks a valid :class:`email.message.Message`."""
    testMessage = Message()
    testMessage.add_header("Message-ID", "abcdefgäöüß§")
    testMessage.add_header("Subject", "This a test SUBJEcT line äöüß§")
    testMessage.add_header("Date", "Fri, 09 Nov 2001 01:08:47 -0000")
    testMessage.add_header("test", "test äöüß§")
    testMessage.add_header("multi", "test")
    testMessage.add_header("multi", "äöüß§\t")
    testMessage.add_header("multi", "123456")
    return testMessage


@pytest.fixture(name="mock_special_mailMessage", scope="module")
def fixture_mock_special_mailMessage():
    """Mocks a valid :class:`email.message.Message` with special contents."""
    testMessage = Message()
    testMessage.add_header("Subject", "This a test SUBJEcT line äöüß§ \t ")
    return testMessage


@pytest.fixture(name="mock_bad_mailMessage", scope="module")
def fixture_mock_bad_mailMessage():
    """Mocks an invalid :class:`email.message.Message`."""
    testMessage = Message()
    return testMessage


@pytest.fixture(name="mock_no_mailMessage", scope="module")
def fixture_mock_no_mailMessage():
    """Mocks a none message."""
    testMessage = None
    return testMessage


# pylint: disable=protected-access ; protected members need to be tested as well
@pytest.mark.parametrize("testHeader, expectedResult", [("test äöüß§", "test äöüß§")])
def test__decodeHeader(mock_logger, testHeader, expectedResult):
    decodedHeader = core.utils.mailParsing._decodeHeader(testHeader)
    assert decodedHeader == expectedResult


# pylint: enable=protected-access
