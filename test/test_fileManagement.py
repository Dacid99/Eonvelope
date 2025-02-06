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
    :func:`fixture_mock_empty_parsedMailDict`: Mocks a valid parsedMail dictionary without images or attachments.
    :func:`fixture_mock_empty_parsedMailDict`: Mocks an invalid parsedMail dictionary.
    :func:`fixture_mock_getSubdirectory`: Mocks the :func:`core.models.StorageModel.getSubdirectory` function call.
    :func:`fixture_mock_filesystem`: Mocks a Linux filesystem for realistic testing.
"""
from __future__ import annotations

import email.message
import os
from typing import TYPE_CHECKING
from unittest.mock import call

import pytest
from pyfakefs.fake_filesystem_unittest import Patcher

import core.utils.fileManagment
from core.constants import ParsedMailKeys

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


@pytest.mark.django_db
@pytest.mark.parametrize("PRERENDER_IMAGETYPE", [("png"), ("jpg"), ("tiff")])
def test_getPrerenderImageStoragePath_goodDict(
    mock_logger: MagicMock,
    mock_getSubdirectory: MagicMock,
    PRERENDER_IMAGETYPE: str,
    mocker: MockerFixture,
    override_config,
    mock_good_parsedMailDict: dict,
):
    """Tests :func:`core.utils.fileManagment.getPrerenderImageStoragePath`.

    Args:
        mock_logger: The mocked logger fixture.
        mock_getSubdirectory: The patched call to :func:`core.utils.fileManagment.StorageModel.getSubdirectory`.
            Returns the constant value set in :attr:`getSubDirectoryReturnValue`.
        PRERENDER_IMAGETYPE: The PRERENDER_IMAGETYPE parameter.
        mocker: The general mocker instance.
        mock_good_parsedMailDict: The bad parsedMail dictionary fixture.
    """
    spy_ospathjoin = mocker.spy(os.path, "join")

    with override_config(PRERENDER_IMAGETYPE=PRERENDER_IMAGETYPE):
        prerenderFilePath = core.utils.fileManagment.getPrerenderImageStoragePath(
            mock_good_parsedMailDict
        )

    assert (
        prerenderFilePath
        == f"{patch_getSubDirectory_returnValue}/{mock_messageIDValue}.{PRERENDER_IMAGETYPE}"
    )
    mock_getSubdirectory.assert_called_once()
    spy_ospathjoin.assert_called_with(
        patch_getSubDirectory_returnValue,
        f"{mock_messageIDValue}.{PRERENDER_IMAGETYPE}",
    )
    assert (
        mock_good_parsedMailDict[ParsedMailKeys.PRERENDER_FILE_PATH]
        == prerenderFilePath
    )
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_getPrerenderImageStoragePath_badDict(
    mock_logger: MagicMock,
    mock_getSubdirectory: MagicMock,
    mocker: MockerFixture,
    mock_bad_parsedMailDict: dict,
):
    """Tests :func:`core.utils.fileManagment.getPrerenderImageStoragePath`.

    Args:
        mock_logger: The mocked logger fixture.
        mock_getSubdirectory: The patched call to :func:`core.utils.fileManagment.StorageModel.getSubdirectory`.
            Returns the constant value set in :attr:`getSubDirectoryReturnValue`.
        mocker: The general mocker instance.
        mock_bad_parsedMailDict: The bad parsedMail dictionary fixture.
    """
    spy_ospathjoin = mocker.spy(os.path, "join")

    with pytest.raises(KeyError):
        prerenderFilePath = core.utils.fileManagment.getPrerenderImageStoragePath(
            mock_bad_parsedMailDict
        )

    mock_getSubdirectory.assert_not_called()
    spy_ospathjoin.assert_not_called()
    mock_logger.debug.assert_called()
    assert ParsedMailKeys.PRERENDER_FILE_PATH not in mock_bad_parsedMailDict
