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

"""Test module for the settings of Emailkasten."""

import logging.config

import pytest

from Emailkasten.settings import LOG_DIRECTORY_PATH, LOGGING


@pytest.fixture
def fake_message(faker):
    return faker.sentence()


@pytest.fixture
def production_logging(fake_fs):
    logging.config.dictConfig(LOGGING)


def test_emailkasten_logging(capsys, fake_message, production_logging):
    core_logger = logging.getLogger("Emailkasten")

    core_logger.info(fake_message)

    assert fake_message in capsys.readouterr().err
    with open(LOG_DIRECTORY_PATH / "emailkasten.log") as logfile:
        assert fake_message in logfile.read()
    with open(LOG_DIRECTORY_PATH / "django.log") as logfile:
        assert fake_message not in logfile.read()


def test_core_logging(capsys, fake_message, production_logging):
    core_logger = logging.getLogger("core")

    core_logger.info(fake_message)

    assert fake_message in capsys.readouterr().err
    with open(LOG_DIRECTORY_PATH / "core.log") as logfile:
        assert fake_message in logfile.read()
    with open(LOG_DIRECTORY_PATH / "emailkasten.log") as logfile:
        assert fake_message in logfile.read()
    with open(LOG_DIRECTORY_PATH / "django.log") as logfile:
        assert fake_message not in logfile.read()


def test_api_logging(capsys, fake_message, production_logging):
    api_logger = logging.getLogger("api")

    api_logger.info(fake_message)

    assert fake_message in capsys.readouterr().err
    with open(LOG_DIRECTORY_PATH / "api.log") as logfile:
        assert fake_message in logfile.read()
    with open(LOG_DIRECTORY_PATH / "emailkasten.log") as logfile:
        assert fake_message in logfile.read()
    with open(LOG_DIRECTORY_PATH / "django.log") as logfile:
        assert fake_message not in logfile.read()


def test_web_logging(capsys, fake_message, production_logging):
    web_logger = logging.getLogger("web")

    web_logger.info(fake_message)

    assert fake_message in capsys.readouterr().err
    with open(LOG_DIRECTORY_PATH / "web.log") as logfile:
        assert fake_message in logfile.read()
    with open(LOG_DIRECTORY_PATH / "emailkasten.log") as logfile:
        assert fake_message in logfile.read()
    with open(LOG_DIRECTORY_PATH / "django.log") as logfile:
        assert fake_message not in logfile.read()


def test_django_logging(capsys, fake_message, production_logging):
    django_logger = logging.getLogger("django")

    django_logger.info(fake_message)

    assert fake_message in capsys.readouterr().err
    with open(LOG_DIRECTORY_PATH / "django.log") as logfile:
        assert fake_message in logfile.read()
    with open(LOG_DIRECTORY_PATH / "emailkasten.log") as logfile:
        assert fake_message not in logfile.read()


def test_other_logging(capsys, fake_message, production_logging):
    django_logger = logging.getLogger("other")

    django_logger.info(fake_message)

    assert fake_message in capsys.readouterr().err
    with open(LOG_DIRECTORY_PATH / "emailkasten.log") as logfile:
        assert fake_message in logfile.read()
    with open(LOG_DIRECTORY_PATH / "django.log") as logfile:
        assert fake_message not in logfile.read()
