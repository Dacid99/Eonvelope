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

"""Test module for :mod:`core.signals.save_Account`."""

import pytest
from django.contrib.auth import get_user_model


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """The mocked :attr:`Emailkasten.signals.logger`."""
    return mocker.patch("Emailkasten.signals.logger", autospec=True)


@pytest.mark.django_db
def test_User_post_save_created(faker, mock_logger):
    """Tests the post_save function of :class:`django.contrib.auth.models.User`
    in case the user is newly created.
    """
    new_user = get_user_model().objects.create(
        username=faker.name(), password=faker.password()
    )

    assert hasattr(new_user, "profile")
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_User_post_save_exists(owner_user, mock_logger):
    """Tests the post_save function of :class:`django.contrib.auth.models.User`.
    in case the user already exists.
    """
    assert hasattr(owner_user, "profile")
    pre_logger_calls = mock_logger.debug.call_count

    owner_user.save()

    assert hasattr(owner_user, "profile")
    assert mock_logger.debug.call_count == pre_logger_calls
