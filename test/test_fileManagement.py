# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Test module for :mod:`Emailkasten.fileManagment`.

Fixtures:
    mock_logger: Mocks :attr:`logger` of the module.
    mock_good_parsedMailDict: Mocks a valid parsedMail dictionary used to transport the mail data.
    mock_empty_parsedMailDict: Mocks a valid parsedMail dictionary without images or attachments.
    mock_empty_parsedMailDict: Mocks an invalid parsedMail dictionary.
    mock_filesystem: Mocks a Linux filesystem for realistic testing.
"""
from __future__ import annotations

from typing import TYPE_CHECKING
import email.message
import os
from unittest.mock import call, patch

import pytest
from pyfakefs.fake_filesystem_unittest import Patcher

import Emailkasten.fileManagment
from Emailkasten.constants import ParsedMailKeys

if TYPE_CHECKING:
    from typing import Generator
    from pytest_mock.plugin import MockerFixture
    from unittest.mock import MagicMock
    from pyfakefs.fake_filesystem import FakeFilesystem


patch_getSubDirectory_returnValue = 'unnecessary'
mock_messageIDValue = 'abc123'

@pytest.fixture
def mock_logger(mocker: MockerFixture) -> MagicMock:
    """Mocks :attr:`Emailkasten.fileManagment.logger` of the module."""
    return mocker.patch('Emailkasten.fileManagment.logger')

@pytest.fixture
def mock_good_parsedMailDict() -> dict:
    """Mocks the parsedMail dictionary used to transport the mail data."""
    message = email.message.Message()
    message.add_header('test', "Test message")
    message.set_payload('This is a test mail message.')

    imagePart = email.message.Message()
    imagePart.set_payload('This is supposed to represent some image.')
    mock_imageDict = {
        ParsedMailKeys.Image.FILE_NAME: 'test_imagefilename.png',
        ParsedMailKeys.Image.DATA: imagePart
    }

    attachmentPart = email.message.Message()
    attachmentPart.set_payload('This is supposed to represent some attachment.')
    mock_attachmentDict = {
        ParsedMailKeys.Attachment.FILE_NAME: 'test_attachmentfilename.pdf',
        ParsedMailKeys.Attachment.DATA: attachmentPart
    }

    mock_parsedMailDict = {
        ParsedMailKeys.Header.MESSAGE_ID: mock_messageIDValue,
        ParsedMailKeys.FULL_MESSAGE: message,
        ParsedMailKeys.ATTACHMENTS: [mock_attachmentDict],
        ParsedMailKeys.IMAGES: [mock_imageDict],
    }
    return mock_parsedMailDict

@pytest.fixture
def mock_empty_parsedMailDict() -> dict:
    """Mocks the parsedMail dictionary used to transport the mail data."""
    message = email.message.Message()
    message.add_header('test', "Test message")
    message.set_payload('This is a test mail message.')

    mock_parsedMailDict = {
        ParsedMailKeys.Header.MESSAGE_ID: mock_messageIDValue,
        ParsedMailKeys.FULL_MESSAGE: message,
        ParsedMailKeys.ATTACHMENTS: [],
        ParsedMailKeys.IMAGES: [],
    }
    return mock_parsedMailDict

@pytest.fixture
def mock_bad_parsedMailDict() -> dict:
    """Mocks the parsedMail dictionary used to transport the mail data."""
    return {}

@pytest.fixture
def mock_filesystem() -> Generator[FakeFilesystem, None, None]:
    """Mocks a Linux filesystem for realistic testing.
    Contains different files with various permission settings for the 'other' users and contents .

    Note:
        Fakefs is overly restrictive with os.path.getsize for no-read files!
        Cannot test the behaviour for non-empty no-read files.

    Yields:
        FakeFilesystem: The mock filesystem.
    """
    with Patcher() as patcher:
        if not patcher.fs:
            raise OSError("Generator could not create a fakefs!")

        patcher.fs.create_dir("/dir")
        patcher.fs.chmod("/dir", 0o777)

        patcher.fs.create_file("/dir/full_file", contents="Im not empty!")
        patcher.fs.create_file("/dir/empty_file", contents="")

        def brokenFileSideEffect(file):
            raise OSError
        patcher.fs.create_file("/dir/broken_file", contents="", side_effect=brokenFileSideEffect)

        patcher.fs.create_file("/dir/no_write_file", contents="")
        patcher.fs.chmod("/dir/no_write_file", 0o555)

        patcher.fs.create_file("/dir/no_read_file", contents="")
        patcher.fs.chmod("/dir/no_read_file", 0o333)

        patcher.fs.create_file("/dir/no_readwrite_file", contents="")
        patcher.fs.chmod("/dir/no_readwrite_file", 0o111)

        patcher.fs.create_file("/dir/no_access_file", contents="")
        patcher.fs.chmod("/dir/no_access_file", 0o000)

        patcher.fs.create_dir("/no_access_dir")
        patcher.fs.create_file("/no_access_dir/file", contents="")
        patcher.fs.chmod("/no_access_dir", 0o000)

        yield patcher.fs


@pytest.mark.parametrize(
    "fakeFile, expectedFileExists, expectedFileSize, expectedEMLFilePath, expectedCallsToOpen, expectedErrors",
    [
        ("/dir/new_file", True, 48, "/dir/new_file", 1, 0),
        ("/dir/full_file", True, 13, "/dir/full_file", 0, 0),
        ("/dir/empty_file", True, 48, "/dir/empty_file", 1, 0),
        ("/dir/broken_file", True, 0, None, 2, 2),
        ("/dir/no_write_file", True, 0, None, 1, 1),
        ("/dir/no_read_file", True, 48, "/dir/no_read_file", 1, 0),
        ("/dir/no_readwrite_file", True, 0, None, 1, 1),
        ("/dir/no_access_file", True, 0, None, 1, 1),
        ("/no_access_dir/new_file", False, 0, None, 1, 1),
        ("/no_access_dir/file", True, 0, None, 1, 1),
    ],
)
@patch(
    "Emailkasten.fileManagment.StorageModel.getSubdirectory",
    return_value=patch_getSubDirectory_returnValue,
)
def test_storeMessageAsEML_goodDict(
    mock_storageModel: MagicMock,
    mocker: MockerFixture,
    mock_logger: MagicMock,
    mock_filesystem: FakeFilesystem,
    mock_good_parsedMailDict: dict,
    fakeFile: str,
    expectedFileExists: bool,
    expectedFileSize: int,
    expectedEMLFilePath: str,
    expectedCallsToOpen: int,
    expectedErrors: int,
) -> None:
    """Tests :func:`Emailkasten.fileManagment.storeMessageAsEML` with the help of a fakefs.

    Args:
        mock_storageModel: The patched call to :func:`Emailkasten.fileManagment.StorageModel.getSubdirectory`.
            Returns the constant value set in :attr:`getSubDirectoryReturnValue`.
        mocker: The general mocker instance.
        mock_logger: The mocked logger fixture.
        mock_filesystem : The fakefs fixture.
        mock_parsedMailDict: The parsedMail dictionary fixture.
        fakeFile: The fakeFilePath parameter.
        expectedFileExists: The expectedFileExists parameter.
        expectedFileSize: The expectedFileSize parameter.
        expectedEMLFilePath: The expectedEMLFilePath parameter.
        expectedCallsToOpen: The expectedCallsToOpen parameter.
        expectedErrors: The expectedErrors parameter.

    Note:
        Fakefs is overly restrictive with os.path.getsize for no-read files!
        Cannot test the behaviour for non-empty no-read files.
    """
    mock_ospathjoin = mocker.patch('os.path.join', return_value = fakeFile)
    spy_open = mocker.spy(Emailkasten.fileManagment, 'open')

    Emailkasten.fileManagment.storeMessageAsEML(mock_good_parsedMailDict)

    mock_storageModel.assert_called_once()
    mock_ospathjoin.assert_called_once_with(patch_getSubDirectory_returnValue, mock_messageIDValue + '.eml')

    mock_filesystem.chmod(os.path.dirname(fakeFile), 0o777)
    assert mock_filesystem.exists(fakeFile) is expectedFileExists
    if mock_filesystem.exists(fakeFile):
        mock_filesystem.chmod(fakeFile, 0o666)
        assert mock_filesystem.get_object(fakeFile).size == expectedFileSize

    assert mock_good_parsedMailDict.get(ParsedMailKeys.EML_FILE_PATH) == expectedEMLFilePath
    assert spy_open.call_count == expectedCallsToOpen
    spy_open.assert_has_calls( [call(fakeFile, "wb")] * expectedCallsToOpen )
    assert mock_logger.error.call_count == expectedErrors

    mock_logger.debug.assert_called()



@pytest.mark.parametrize(
    "fakeFile, expectedFileExists, expectedFileSize, expectedFilePath, expectedCallsToOpen, expectedErrors",
    [
        ("/dir/new_file", True, 41, "/dir/new_file", 1, 0),
        ("/dir/full_file", True, 13, "/dir/full_file", 0, 0),
        ("/dir/empty_file", True, 41, "/dir/empty_file", 1, 0),
        ("/dir/broken_file", True, 0, None, 2, 2),
        ("/dir/no_write_file", True, 0, None, 1, 1),
        ("/dir/no_read_file", True, 41, "/dir/no_read_file", 1, 0),
        ("/dir/no_readwrite_file", True, 0, None, 1, 1),
        ("/dir/no_access_file", True, 0, None, 1, 1),
        ("/no_access_dir/new_file", False, 0, None, 1, 1),
        ("/no_access_dir/file", True, 0, None, 1, 1),
    ],
)
@patch(
    "Emailkasten.fileManagment.StorageModel.getSubdirectory",
    return_value=patch_getSubDirectory_returnValue,
)
def test_storeImages_goodDict(
    mock_storageModel: MagicMock,
    mocker: MockerFixture,
    mock_logger: MagicMock,
    mock_filesystem: FakeFilesystem,
    mock_good_parsedMailDict: dict,
    fakeFile: str,
    expectedFileExists: bool,
    expectedFileSize: int,
    expectedFilePath: str,
    expectedCallsToOpen: int,
    expectedErrors: int,
) -> None:
    """Tests :func:`Emailkasten.fileManagment.storeImages` with the help of a fakefs.

    Args:
        mock_storageModel: The patched call to :func:`Emailkasten.fileManagment.StorageModel.getSubdirectory`.
            Returns the constant value set in :attr:`getSubDirectoryReturnValue`.
        mocker: The general mocker instance.
        mock_logger: The mocked logger fixture.
        mock_filesystem : The fakefs fixture.
        mock_good_parsedMailDict: The parsedMail dictionary fixture.
        fakeFile: The fakeFilePath parameter.
        expectedFileExists: The expectedFileExists parameter.
        expectedFileSize: The expectedFileSize parameter.
        expectedFilePath: The expectedFilePath parameter.
        expectedCallsToOpen: The expectedCallsToOpen parameter.
        expectedErrors: The expectedErrors parameter.

    Note:
        Fakefs is overly restrictive with os.path.getsize for no-read files!
        Cannot test the behaviour for non-empty no-read files.
    """
    mock_ospathjoin = mocker.patch('os.path.join', return_value = fakeFile)
    spy_open = mocker.spy(Emailkasten.fileManagment, 'open')

    Emailkasten.fileManagment.storeImages(mock_good_parsedMailDict)

    mock_storageModel.assert_called_once()
    mock_ospathjoin.assert_called_once_with(patch_getSubDirectory_returnValue, 'test_imagefilename.png')

    mock_filesystem.chmod(os.path.dirname(fakeFile), 0o777)
    assert mock_filesystem.exists(fakeFile) is expectedFileExists
    if mock_filesystem.exists(fakeFile):
        mock_filesystem.chmod(fakeFile, 0o666)
        assert mock_filesystem.get_object(fakeFile).size == expectedFileSize

    assert mock_good_parsedMailDict[ParsedMailKeys.IMAGES][0].get(ParsedMailKeys.Image.FILE_PATH) == expectedFilePath
    assert spy_open.call_count == expectedCallsToOpen
    spy_open.assert_has_calls( [call(fakeFile, "wb")] * expectedCallsToOpen )
    assert mock_logger.error.call_count == expectedErrors

    mock_logger.debug.assert_called()


@patch(
    "Emailkasten.fileManagment.StorageModel.getSubdirectory",
    return_value=patch_getSubDirectory_returnValue,
)
def test_storeImages_emptyDict(
    mock_storageModel: MagicMock,
    mocker: MockerFixture,
    mock_logger: MagicMock,
    mock_filesystem: FakeFilesystem,
    mock_empty_parsedMailDict: dict
) -> None:
    """Tests :func:`Emailkasten.fileManagment.storeImages` with the help of a fakefs.

    Args:
        mock_storageModel: The patched call to :func:`Emailkasten.fileManagment.StorageModel.getSubdirectory`.
            Returns the constant value set in :attr:`getSubDirectoryReturnValue`.
        mocker: The general mocker instance.
        mock_logger: The mocked logger fixture.
        mock_filesystem : The fakefs fixture.
        mock_bad_parsedMailDict: The parsedMail dictionary fixture.

    Note:
        Fakefs is overly restrictive with os.path.getsize for no-read files!
        Cannot test the behaviour for non-empty no-read files.
    """
    fakeFile = '/dir/new_file'
    mock_ospathjoin = mocker.patch('os.path.join', return_value = fakeFile)
    spy_open = mocker.spy(Emailkasten.fileManagment, 'open')

    Emailkasten.fileManagment.storeImages(mock_empty_parsedMailDict)

    mock_storageModel.assert_not_called()
    mock_ospathjoin.assert_not_called()

    mock_filesystem.chmod(os.path.dirname(fakeFile), 0o777)
    assert mock_filesystem.exists(fakeFile) is False

    assert mock_empty_parsedMailDict[ParsedMailKeys.IMAGES] == []
    assert spy_open.call_count == 0

    mock_logger.debug.assert_called()


@patch(
    "Emailkasten.fileManagment.StorageModel.getSubdirectory",
    return_value=patch_getSubDirectory_returnValue,
)
def test_storeImages_badDict(
    mock_storageModel: MagicMock,
    mocker: MockerFixture,
    mock_logger: MagicMock,
    mock_filesystem: FakeFilesystem,
    mock_bad_parsedMailDict: dict
) -> None:
    """Tests :func:`Emailkasten.fileManagment.storeImages` with the help of a fakefs.

    Args:
        mock_storageModel: The patched call to :func:`Emailkasten.fileManagment.StorageModel.getSubdirectory`.
            Returns the constant value set in :attr:`getSubDirectoryReturnValue`.
        mocker: The general mocker instance.
        mock_logger: The mocked logger fixture.
        mock_filesystem : The fakefs fixture.
        mock_bad_parsedMailDict: The parsedMail dictionary fixture.

    Note:
        Fakefs is overly restrictive with os.path.getsize for no-read files!
        Cannot test the behaviour for non-empty no-read files.
    """
    fakeFile = '/dir/new_file'
    mock_ospathjoin = mocker.patch('os.path.join', return_value = fakeFile)

    spy_open = mocker.spy(Emailkasten.fileManagment, 'open')

    with pytest.raises(KeyError):
        Emailkasten.fileManagment.storeImages(mock_bad_parsedMailDict)

    mock_storageModel.assert_not_called()
    mock_ospathjoin.assert_not_called()

    mock_filesystem.chmod(os.path.dirname(fakeFile), 0o777)
    assert mock_filesystem.exists(fakeFile) is False

    with pytest.raises(KeyError):
        mock_bad_parsedMailDict[ParsedMailKeys.IMAGES]

    assert spy_open.call_count == 0


@pytest.mark.parametrize(
    "fakeFile, expectedFileExists, expectedFileSize, expectedFilePath, expectedCallsToOpen, expectedErrors",
    [
        ("/dir/new_file", True, 46, "/dir/new_file", 1, 0),
        ("/dir/full_file", True, 13, "/dir/full_file", 0, 0),
        ("/dir/empty_file", True, 46, "/dir/empty_file", 1, 0),
        ("/dir/broken_file", True, 0, None, 2, 2),
        ("/dir/no_write_file", True, 0, None, 1, 1),
        ("/dir/no_read_file", True, 46, "/dir/no_read_file", 1, 0),
        ("/dir/no_readwrite_file", True, 0, None, 1, 1),
        ("/dir/no_access_file", True, 0, None, 1, 1),
        ("/no_access_dir/new_file", False, 0, None, 1, 1),
        ("/no_access_dir/file", True, 0, None, 1, 1),
    ],
)
@patch(
    "Emailkasten.fileManagment.StorageModel.getSubdirectory",
    return_value=patch_getSubDirectory_returnValue,
)
def test_storeAttachments_goodDict(
    mock_storageModel: MagicMock,
    mocker: MockerFixture,
    mock_logger: MagicMock,
    mock_filesystem: FakeFilesystem,
    mock_good_parsedMailDict: dict,
    fakeFile: str,
    expectedFileExists: bool,
    expectedFileSize: int,
    expectedFilePath: str,
    expectedCallsToOpen: int,
    expectedErrors: int,
) -> None:
    """Tests :func:`Emailkasten.fileManagment.storeAttachments` with the help of a fakefs.

    Args:
        mock_storageModel: The patched call to :func:`Emailkasten.fileManagment.StorageModel.getSubdirectory`.
            Returns the constant value set in :attr:`getSubDirectoryReturnValue`.
        mocker: The general mocker instance.
        mock_logger: The mocked logger fixture.
        mock_filesystem : The fakefs fixture.
        mock_parsedMailDict: The parsedMail dictionary fixture.
        fakeFile: The fakeFilePath parameter.
        expectedFileExists: The expectedFileExists parameter.
        expectedFileSize: The expectedFileSize parameter.
        expectedFilePath: The expectedFilePath parameter.
        expectedCallsToOpen: The expectedCallsToOpen parameter.
        expectedErrors: The expectedErrors parameter.

    Note:
        Fakefs is overly restrictive with os.path.getsize for no-read files!
        Cannot test the behaviour for non-empty no-read files.
    """
    mock_ospathjoin = mocker.patch('os.path.join', return_value = fakeFile)
    spy_open = mocker.spy(Emailkasten.fileManagment, 'open')

    Emailkasten.fileManagment.storeAttachments(mock_good_parsedMailDict)

    mock_storageModel.assert_called_once()
    mock_ospathjoin.assert_called_once_with(patch_getSubDirectory_returnValue, 'test_attachmentfilename.pdf')

    mock_filesystem.chmod(os.path.dirname(fakeFile), 0o777)
    assert mock_filesystem.exists(fakeFile) is expectedFileExists
    if mock_filesystem.exists(fakeFile):
        mock_filesystem.chmod(fakeFile, 0o666)
        assert mock_filesystem.get_object(fakeFile).size == expectedFileSize

    assert mock_good_parsedMailDict[ParsedMailKeys.ATTACHMENTS][0].get(ParsedMailKeys.Attachment.FILE_PATH) == expectedFilePath
    assert spy_open.call_count == expectedCallsToOpen
    spy_open.assert_has_calls( [call(fakeFile, "wb")] * expectedCallsToOpen )
    assert mock_logger.error.call_count == expectedErrors

    mock_logger.debug.assert_called()


@patch(
    "Emailkasten.fileManagment.StorageModel.getSubdirectory",
    return_value=patch_getSubDirectory_returnValue,
)
def test_storeAttachments_emptyDict(
    mock_storageModel: MagicMock,
    mocker: MockerFixture,
    mock_logger: MagicMock,
    mock_filesystem: FakeFilesystem,
    mock_empty_parsedMailDict: dict
) -> None:
    """Tests :func:`Emailkasten.fileManagment.storeAttachments` with the help of a fakefs.

    Args:
        mock_storageModel: The patched call to :func:`Emailkasten.fileManagment.StorageModel.getSubdirectory`.
            Returns the constant value set in :attr:`getSubDirectoryReturnValue`.
        mocker: The general mocker instance.
        mock_logger: The mocked logger fixture.
        mock_filesystem : The fakefs fixture.
        mock_bad_parsedMailDict: The parsedMail dictionary fixture.

    Note:
        Fakefs is overly restrictive with os.path.getsize for no-read files!
        Cannot test the behaviour for non-empty no-read files.
    """
    fakeFile = '/dir/new_file'
    mock_ospathjoin = mocker.patch('os.path.join', return_value = fakeFile)
    spy_open = mocker.spy(Emailkasten.fileManagment, 'open')

    Emailkasten.fileManagment.storeAttachments(mock_empty_parsedMailDict)

    mock_storageModel.assert_not_called()
    mock_ospathjoin.assert_not_called()

    mock_filesystem.chmod(os.path.dirname(fakeFile), 0o777)
    assert mock_filesystem.exists(fakeFile) is False

    assert mock_empty_parsedMailDict[ParsedMailKeys.ATTACHMENTS] == []
    assert spy_open.call_count == 0

    mock_logger.debug.assert_called()


@patch(
    "Emailkasten.fileManagment.StorageModel.getSubdirectory",
    return_value=patch_getSubDirectory_returnValue,
)
def test_storeAttachments_badDict(
    mock_storageModel: MagicMock,
    mocker: MockerFixture,
    mock_logger: MagicMock,
    mock_filesystem: FakeFilesystem,
    mock_bad_parsedMailDict: dict
) -> None:
    """Tests :func:`Emailkasten.fileManagment.storeAttachments` with the help of a fakefs.

    Args:
        mock_storageModel: The patched call to :func:`Emailkasten.fileManagment.StorageModel.getSubdirectory`.
            Returns the constant value set in :attr:`getSubDirectoryReturnValue`.
        mocker: The general mocker instance.
        mock_logger: The mocked logger fixture.
        mock_filesystem : The fakefs fixture.
        mock_bad_parsedMailDict: The parsedMail dictionary fixture.

    Note:
        Fakefs is overly restrictive with os.path.getsize for no-read files!
        Cannot test the behaviour for non-empty no-read files.
    """
    fakeFile = '/dir/new_file'
    mock_ospathjoin = mocker.patch('os.path.join', return_value = fakeFile)

    spy_open = mocker.spy(Emailkasten.fileManagment, 'open')

    with pytest.raises(KeyError):
        Emailkasten.fileManagment.storeAttachments(mock_bad_parsedMailDict)

    mock_storageModel.assert_not_called()
    mock_ospathjoin.assert_not_called()

    mock_filesystem.chmod(os.path.dirname(fakeFile), 0o777)
    assert mock_filesystem.exists(fakeFile) is False

    with pytest.raises(KeyError):
        mock_bad_parsedMailDict[ParsedMailKeys.ATTACHMENTS]

    assert spy_open.call_count == 0
