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

"""Test module for :mod:`core.utils.fileManagment`.

Fixtures:
    :func:`fixture_mock_logger`: Mocks :attr:`logger` of the module.
    :func:`fixture_mock_good_parsedMailDict`: Mocks a valid parsedMail dictionary used to transport the mail data.
    :func:`fixture_mock_empty_parsedMailDict`: Mocks a valid parsedMail dictionary without attachments.
    :func:`fixture_mock_empty_parsedMailDict`: Mocks an invalid parsedMail dictionary.
    :func:`fixture_mock_getSubdirectory`: Mocks the :func:`core.models.StorageModel.getSubdirectory` function call.
    :func:`fixture_mock_filesystem`: Mocks a Linux filesystem for realistic testing.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from pyfakefs.fake_filesystem_unittest import Patcher

import core.utils.fileManagment
from core.constants import HeaderFields

if TYPE_CHECKING:
    from typing import Generator
    from unittest.mock import MagicMock

    from pyfakefs.fake_filesystem import FakeFilesystem
    from pytest_mock.plugin import MockerFixture


patch_getSubDirectory_returnValue = "subDirInStorage"
mock_messageIDValue = "abc123"


@pytest.fixture(name="mock_logger", autouse=True)
def fixture_mock_logger(mocker: MockerFixture) -> MagicMock:
    """Mocks :attr:`core.utils.fileManagment.logger` of the module."""
    return mocker.patch("core.utils.fileManagment.logger")


@pytest.fixture(name="mock_getSubdirectory", autouse=True)
def fixture_mock_getSubdirectory(mocker: MockerFixture) -> MagicMock:
    """Mocks the :func:`core.models.StorageModel.StorageModel.getSubdirectory` function."""
    return mocker.patch(
        "core.utils.fileManagment.StorageModel.getSubdirectory",
        return_value=patch_getSubDirectory_returnValue,
    )


@pytest.fixture(name="mock_filesystem", autouse=True)
def fixture_mock_filesystem() -> Generator[FakeFilesystem, None, None]:
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

        patcher.fs.create_file(
            "/dir/broken_file", contents="", side_effect=brokenFileSideEffect
        )

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
    "fakeFile, expectedFileExists, expectedFileSize, expectedCallsToOpen, expectedErrors",
    [
        ("/dir/new_file", True, 28, 1, 0),
        ("/dir/full_file", True, 13, 0, 0),
        ("/dir/empty_file", True, 28, 1, 0),
        ("/dir/broken_file", True, 0, 2, 2),
        ("/dir/no_write_file", True, 0, 1, 1),
        ("/dir/no_read_file", True, 28, 1, 0),
        ("/dir/no_readwrite_file", True, 0, 1, 1),
        ("/dir/no_access_file", True, 0, 1, 1),
        ("/no_access_dir/new_file", False, 0, 1, 1),
        ("/no_access_dir/file", True, 0, 1, 1),
    ],
)
def test_saveStore(
    mocker: MockerFixture,
    mock_logger: MagicMock,
    mock_filesystem: FakeFilesystem,
    fakeFile: str,
    expectedFileExists: bool,
    expectedFileSize: int,
    expectedCallsToOpen: int,
    expectedErrors: int,
) -> None:
    """Tests :func:`core.utils.fileManagment.saveStore` with the help of a fakefs.

    Args:
        mocker: The general mocker instance.
        mock_logger: The mocked logger fixture.
        mock_filesystem: The fakefs fixture.
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
    spy_open = mocker.spy(core.utils.fileManagment, "open")
    content = b"This is 28bytes for testing."

    @core.utils.fileManagment.saveStore
    def test_save(file):
        file.write(content)

    test_save(fakeFile)

    mock_filesystem.chmod(os.path.dirname(fakeFile), 0o777)
    assert mock_filesystem.exists(fakeFile) is expectedFileExists
    if mock_filesystem.exists(fakeFile):
        mock_filesystem.chmod(fakeFile, 0o666)
        assert mock_filesystem.get_object(fakeFile).size == expectedFileSize

    assert spy_open.call_count == expectedCallsToOpen
    spy_open.assert_has_calls([mocker.call(fakeFile, "wb")] * expectedCallsToOpen)
    assert mock_logger.error.call_count == expectedErrors

    mock_logger.debug.assert_called()
