# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
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

"""Test module for :mod:`eonvelope.models.UserProfile`."""

import pytest

from eonvelope.models import UserProfile


@pytest.mark.django_db
def test_UserProfile_fields(owner_user):
    """Tests the fields of :class:`eonvelope.models.UserProfile`."""

    assert owner_user.profile.paperless_url is not None
    assert isinstance(owner_user.profile.paperless_url, str)
    assert owner_user.profile.paperless_api_key is not None
    assert isinstance(owner_user.profile.paperless_api_key, str)
    assert owner_user.profile.paperless_tika_enabled is False
    assert owner_user.profile.immich_url is not None
    assert isinstance(owner_user.profile.immich_url, str)
    assert owner_user.profile.immich_api_key is not None
    assert isinstance(owner_user.profile.immich_api_key, str)
    assert owner_user.profile.nextcloud_url is not None
    assert isinstance(owner_user.profile.nextcloud_url, str)
    assert owner_user.profile.nextcloud_username is not None
    assert isinstance(owner_user.profile.nextcloud_username, str)
    assert owner_user.profile.nextcloud_password is not None
    assert isinstance(owner_user.profile.nextcloud_addressbook, str)
    assert owner_user.profile.nextcloud_addressbook == "contacts"


@pytest.mark.django_db
def test_UserProfile___str__(owner_user):
    """Tests the string representation of :class:`eonvelope.models.UserProfile`."""
    assert owner_user.username in str(owner_user.profile)


@pytest.mark.django_db
def test_UserProfile_foreign_key_deletion(owner_user):
    """Tests the on_delete foreign key constraint in :class:`eonvelope.models.UserProfile`."""

    assert owner_user.profile is not None
    owner_user.delete()
    with pytest.raises(UserProfile.DoesNotExist):
        owner_user.profile.refresh_from_db()
