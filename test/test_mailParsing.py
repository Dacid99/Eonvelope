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
    return mocker.patch('core.utils.mailParsing.logger')

@pytest.fixture(name="mock_good_mailMessage", scope='module')
def fixture_mock_good_mailMessage():
    """Mocks a valid :class:`email.message.Message`."""
    testMessage = Message()
    testMessage.add_header("Message-ID", 'abcdefgäöüß§')
    testMessage.add_header("Subject", 'This a test SUBJEcT line äöüß§')
    testMessage.add_header("Date", 'Fri, 09 Nov 2001 01:08:47 -0000')
    testMessage.add_header("test", 'test äöüß§')
    testMessage.add_header("multi", 'test')
    testMessage.add_header("multi", 'äöüß§\t')
    testMessage.add_header("multi", '123456')
    return testMessage

@pytest.fixture(name="mock_special_mailMessage", scope='module')
def fixture_mock_special_mailMessage():
    """Mocks a valid :class:`email.message.Message` with special contents."""
    testMessage = Message()
    testMessage.add_header("Subject", 'This a test SUBJEcT line äöüß§ \t ')
    return testMessage

@pytest.fixture(name="mock_bad_mailMessage", scope='module')
def fixture_mock_bad_mailMessage():
    """Mocks an invalid :class:`email.message.Message`."""
    testMessage = Message()
    return testMessage

@pytest.fixture(name="mock_no_mailMessage", scope='module')
def fixture_mock_no_mailMessage():
    """Mocks a none message."""
    testMessage = None
    return testMessage

@pytest.fixture(name="mock_empty_parsedMailDict")
def fixture_mock_empty_parsedMailDict():
    """Mocks an empty parsedMail :class:`dict` that the mail is parsed into."""
    return {}

# pylint: disable=protected-access ; protected members need to be tested as well
@pytest.mark.parametrize(
    'testHeader, expectedResult',
    [
        ('test äöüß§', "test äöüß§")
    ]
)
def test__decodeHeader(mock_logger, testHeader, expectedResult):
    decodedHeader = core.utils.mailParsing._decodeHeader(testHeader)
    assert decodedHeader == expectedResult


@pytest.mark.parametrize(
        'testMailers, expectedResult, warningCalled',
        [
            (["Test äöüß§ <test@testdomain.tld>"], [("Test äöüß§", "test@testdomain.tld")], False),
            (["Test Persön <testtestdomain.tld>"], [("Test Persön", "testtestdomain.tld")], True),
            (["test@testdomain.tld"], [("", "test@testdomain.tld")], False)
        ])
def test__separateRFC2822MailAddressFormat(mock_logger, testMailers, expectedResult, warningCalled):
    separatedMailers = core.utils.mailParsing._separateRFC2822MailAddressFormat(testMailers)

    assert separatedMailers == expectedResult


def test__parseMessageID_success(mock_logger, mock_good_mailMessage, mock_empty_parsedMailDict):
    core.utils.mailParsing._parseMessageID(mock_good_mailMessage, mock_empty_parsedMailDict)
    assert core.constants.ParsedMailKeys.Header.MESSAGE_ID in mock_empty_parsedMailDict
    assert mock_empty_parsedMailDict[core.constants.ParsedMailKeys.Header.MESSAGE_ID] == 'abcdefgäöüß§'
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


def test__parseMessageID_emptyMessage(mock_logger, mock_bad_mailMessage, mock_empty_parsedMailDict):
    core.utils.mailParsing._parseMessageID(mock_bad_mailMessage, mock_empty_parsedMailDict)
    assert core.constants.ParsedMailKeys.Header.MESSAGE_ID in mock_empty_parsedMailDict
    assert mock_empty_parsedMailDict[core.constants.ParsedMailKeys.Header.MESSAGE_ID] == str(hash(mock_bad_mailMessage))
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_called()
    mock_logger.error.assert_not_called()


def test__parseMessageID_noMessage(mock_no_mailMessage, mock_empty_parsedMailDict):
    with pytest.raises(AttributeError):
        core.utils.mailParsing._parseMessageID(mock_no_mailMessage, mock_empty_parsedMailDict)



def test__parseDate_success(mock_logger, mock_good_mailMessage, mock_empty_parsedMailDict):
    core.utils.mailParsing._parseDate(mock_good_mailMessage, mock_empty_parsedMailDict)
    assert core.constants.ParsedMailKeys.Header.DATE in mock_empty_parsedMailDict
    assert mock_empty_parsedMailDict[core.constants.ParsedMailKeys.Header.DATE] == datetime.datetime(2001, 11, 9, 1, 8, 47)
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


def test__parseDate_emptyMessage(mock_logger, mock_bad_mailMessage, mock_empty_parsedMailDict):
    core.utils.mailParsing._parseDate(mock_bad_mailMessage, mock_empty_parsedMailDict)
    assert core.constants.ParsedMailKeys.Header.DATE in mock_empty_parsedMailDict
    assert mock_empty_parsedMailDict[core.constants.ParsedMailKeys.Header.DATE] == datetime.datetime(1971, 1, 1, 0, 0, 0)
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_called()
    mock_logger.error.assert_not_called()


def test__parseDate_noMessage(mock_no_mailMessage, mock_empty_parsedMailDict):
    with pytest.raises(AttributeError):
        core.utils.mailParsing._parseDate(mock_no_mailMessage, mock_empty_parsedMailDict)


@pytest.mark.parametrize(
    "stripTexts, expectedResult",
    [(True, "This a test SUBJEcT line äöüß§"), (False, "This a test SUBJEcT line äöüß§ \t ")],
)
def test__parseSubject_success(mock_logger, stripTexts, expectedResult, mocker, mock_special_mailMessage, mock_empty_parsedMailDict):
    mock_parsingConfiguration = mocker.patch('core.utils.mailParsing.ParsingConfiguration')
    mock_parsingConfiguration.STRIP_TEXTS = stripTexts
    core.utils.mailParsing._parseSubject(mock_special_mailMessage, mock_empty_parsedMailDict)
    assert core.constants.ParsedMailKeys.Header.SUBJECT in mock_empty_parsedMailDict
    assert mock_empty_parsedMailDict[core.constants.ParsedMailKeys.Header.SUBJECT] == expectedResult
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


def test__parseSubject_emptyMessage(mock_logger, mock_bad_mailMessage, mock_empty_parsedMailDict):
    core.utils.mailParsing._parseSubject(mock_bad_mailMessage, mock_empty_parsedMailDict)
    assert core.constants.ParsedMailKeys.Header.SUBJECT in mock_empty_parsedMailDict
    assert mock_empty_parsedMailDict[core.constants.ParsedMailKeys.Header.SUBJECT] == ''
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_called()
    mock_logger.error.assert_not_called()


def test__parseSubject_noMessage(mock_no_mailMessage, mock_empty_parsedMailDict):
    with pytest.raises(AttributeError):
        core.utils.mailParsing._parseSubject(mock_no_mailMessage, mock_empty_parsedMailDict)



def test__parseHeader_success(mock_logger, mock_good_mailMessage, mock_empty_parsedMailDict):
    core.utils.mailParsing._parseHeader(mock_good_mailMessage, "test", mock_empty_parsedMailDict)
    assert "test" in mock_empty_parsedMailDict
    assert mock_empty_parsedMailDict["test"] == "test äöüß§"
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


def test__parseHeader_emptyMessage(mock_logger, mock_bad_mailMessage, mock_empty_parsedMailDict):
    core.utils.mailParsing._parseHeader(mock_bad_mailMessage, "test", mock_empty_parsedMailDict)
    assert "test" in mock_empty_parsedMailDict
    assert mock_empty_parsedMailDict["test"] == ''
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


def test__parseHeader_noMessage(mock_no_mailMessage, mock_empty_parsedMailDict):
    with pytest.raises(AttributeError):
        core.utils.mailParsing._parseHeader(mock_no_mailMessage, "test", mock_empty_parsedMailDict)



def test__parseMultipleHeader_success(mock_logger, mock_good_mailMessage, mock_empty_parsedMailDict):
    core.utils.mailParsing._parseMultipleHeader(mock_good_mailMessage, "multi", mock_empty_parsedMailDict)
    assert "multi" in mock_empty_parsedMailDict
    assert mock_empty_parsedMailDict["multi"] == "test\näöüß§\t\n123456"
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


def test__parseMultipleHeader_noneMulti(mock_logger, mock_good_mailMessage, mock_empty_parsedMailDict):
    core.utils.mailParsing._parseMultipleHeader(mock_good_mailMessage, "test", mock_empty_parsedMailDict)
    assert "test" in mock_empty_parsedMailDict
    assert mock_empty_parsedMailDict["test"] == "test äöüß§"
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


def test__parseMultipleHeader_emptyMessage(mock_logger, mock_bad_mailMessage, mock_empty_parsedMailDict):
    core.utils.mailParsing._parseMultipleHeader(mock_bad_mailMessage, "multi", mock_empty_parsedMailDict)
    assert "multi" in mock_empty_parsedMailDict
    assert mock_empty_parsedMailDict["multi"] == ''
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


def test__parseMultipleHeader_noMessage(mock_no_mailMessage, mock_empty_parsedMailDict):
    with pytest.raises(AttributeError):
        core.utils.mailParsing._parseMultipleHeader(mock_no_mailMessage, "multi", mock_empty_parsedMailDict)


def test_parseMail_success(mock_logger, mock_good_mailMessage, mocker):
    mocker.patch('email.message_from_bytes', return_value = mock_good_mailMessage)
    parsedMail = core.utils.mailParsing.parseMail(mock_good_mailMessage)
    for headerName, _ in core.constants.ParsedMailKeys.Header():
        assert headerName in parsedMail

    mock_logger.debug.assert_called()
    #mock_logger.warning.assert_not_called()
    #mock_logger.error.assert_not_called()

# pylint: enable=protected-access
