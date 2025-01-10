from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from model_bakery import baker
from pyfakefs.fake_filesystem_unittest import Patcher

from Emailkasten.Models.StorageModel import StorageModel

if TYPE_CHECKING:
    from typing import Generator
    from unittest.mock import MagicMock

    from pyfakefs.fake_filesystem import FakeFilesystem
    from pytest_mock.plugin import MockerFixture

@pytest.fixture(name='mock_logger', autouse=True)
def fixture_mock_logger(mocker: MockerFixture) -> MagicMock:
    """Mocks :attr:`Emailkasten.Models.StorageModel.logger` of the module."""
    return mocker.patch('Emailkasten.Models.StorageModel.logger')

@pytest.fixture(name='mock_filesystem', autouse=True)
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

        patcher.fs.create_dir("/empty-storage")

        patcher.fs.create_dir("/full-storage")
        patcher.fs.create_file("/full-storage/file", contents="Im not empty!")

        patcher.fs.create_dir("/conflicting-storage/0")
        patcher.fs.create_file("/conflicting-storage/0/test", contents="Im not empty!")

        yield patcher.fs



@pytest.mark.django_db
@pytest.mark.parametrize(
    'STORAGE_PATH, expectedCritical',
    [
        ('empty-storage', False),
        ('full-storage', True),
        ('conflicting-storage', True),
    ]
)
def test_StorageModel_initial_single_creation(STORAGE_PATH, expectedCritical, mock_logger, mock_filesystem, mocker):
    """Tests the correct initial allocation of storage by :class:`Emailkasten.Models.StorageModel.StorageModel`."""

    mock_StorageConfiguration = mocker.patch('Emailkasten.Models.StorageModel.StorageConfiguration')
    mock_StorageConfiguration.STORAGE_PATH = STORAGE_PATH
    mock_StorageConfiguration.MAX_SUBDIRS_PER_DIR = 3

    subdirectory = StorageModel.getSubdirectory('test')

    assert os.path.isdir(subdirectory)
    assert subdirectory == os.path.join(STORAGE_PATH, '0', 'test')
    mock_logger.critical.called = expectedCritical
    mock_logger.info.assert_called()

    assert StorageModel.objects.count() == 1
    storage = StorageModel.objects.get(current=True)
    assert storage.directory_number == 0
    assert storage.path == os.path.dirname(subdirectory)
    assert storage.subdirectory_count == 1


@pytest.mark.django_db
def test_StorageModel_initial_many_creation(STORAGE_PATH, expectedCritical, mock_logger, mock_filesystem, mocker):
    """Tests the correct initial allocation of storage by :class:`Emailkasten.Models.StorageModel.StorageModel`."""

    mock_StorageConfiguration = mocker.patch('Emailkasten.Models.StorageModel.StorageConfiguration')
    mock_StorageConfiguration.STORAGE_PATH = STORAGE_PATH
    mock_StorageConfiguration.MAX_SUBDIRS_PER_DIR = 3

    for i in range(0,2*3+1):
        StorageModel.getSubdirectory(f"test_{i}")

    mock_logger.critical.assert_not_called()
    mock_logger.info.assert_called()

    assert StorageModel.objects.filter(current=True).count() == 1
    assert StorageModel.objects.count() == 3
    assert all(
            storage.subdirectory_count == len(os.listdir(storage.path)) for storage in StorageModel.objects.all()
        )
    storage = StorageModel.objects.get(current=True)
    assert storage.directory_number == 2
    assert storage.subdirectory_count == 1


@pytest.mark.django_db
def test_health_check_success(mock_logger, mock_filesystem, mocker):
    """Tests the correct initial allocation of storage by :class:`Emailkasten.Models.StorageModel.StorageModel`."""

    mock_StorageConfiguration = mocker.patch('Emailkasten.Models.StorageModel.StorageConfiguration')
    mock_StorageConfiguration.STORAGE_PATH = '/empty-storage'
    mock_StorageConfiguration.MAX_SUBDIRS_PER_DIR = 3

    for i in range(0,2*3+1):
        StorageModel.getSubdirectory(f"test_{i}")


    health = StorageModel.healthcheck()

    assert health


@pytest.mark.django_db
def test_health_check_failed_duplicate_current(mock_logger, mock_filesystem, mocker):
    """Tests the correct initial allocation of storage by :class:`Emailkasten.Models.StorageModel.StorageModel`."""

    mock_StorageConfiguration = mocker.patch('Emailkasten.Models.StorageModel.StorageConfiguration')
    mock_StorageConfiguration.STORAGE_PATH = '/empty-storage'
    mock_StorageConfiguration.MAX_SUBDIRS_PER_DIR = 3

    for i in range(0,2*3+1):
        StorageModel.getSubdirectory(f"test_{i}")
    StorageModel.objects.create(directory_number=10, current=True)

    health = StorageModel.healthcheck()

    assert not health
    mock_logger.critical.assert_called()


@pytest.mark.django_db
def test_health_check_failed_dirty_storage(mock_logger, mock_filesystem, mocker):
    """Tests the correct initial allocation of storage by :class:`Emailkasten.Models.StorageModel.StorageModel`."""

    mock_StorageConfiguration = mocker.patch('Emailkasten.Models.StorageModel.StorageConfiguration')
    mock_StorageConfiguration.STORAGE_PATH = '/conflicting-storage'
    mock_StorageConfiguration.MAX_SUBDIRS_PER_DIR = 3

    for i in range(0,2*3+1):
        StorageModel.getSubdirectory(f"test_{i}")

    health = StorageModel.healthcheck()

    assert not health
    mock_logger.critical.assert_called()
