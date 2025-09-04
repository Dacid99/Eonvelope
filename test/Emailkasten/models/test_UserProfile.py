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

"""Test module for :mod:`Emailkasten.models.UserProfile`."""

import pytest

from Emailkasten.models import UserProfile


@pytest.mark.django_db
def test_UserProfile_fields(owner_user):
    """Tests the fields of :class:`Emailkasten.models.UserProfile`."""

    assert owner_user.profile.paperless_url is not None
    assert isinstance(owner_user.profile.paperless_url, str)
    assert owner_user.profile.paperless_api_key is not None
    assert isinstance(owner_user.profile.paperless_api_key, str)
    assert owner_user.profile.paperless_tika_enabled is False


@pytest.mark.django_db
def test_UserProfile___str__(owner_user):
    """Tests the string representation of :class:`Emailkasten.models.UserProfile`."""
    assert owner_user.username in str(owner_user.profile)


@pytest.mark.django_db
def test_UserProfile_foreign_key_deletion(owner_user):
    """Tests the on_delete foreign key constraint in :class:`Emailkasten.models.UserProfile`."""

    assert owner_user.profile is not None
    owner_user.delete()
    with pytest.raises(UserProfile.DoesNotExist):
        owner_user.profile.refresh_from_db()
