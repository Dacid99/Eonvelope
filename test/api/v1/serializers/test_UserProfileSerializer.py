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

"""Test module for :mod:`api.v1.serializers.UserProfileSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.UserProfileSerializer import (
    UserProfileSerializer,
)


@pytest.mark.django_db
def test_output(owner_user, request_context):
    """Tests for the expected output of the serializer."""
    profile = owner_user.profile
    serializer_data = UserProfileSerializer(
        instance=profile, context=request_context
    ).data

    assert "id" not in serializer_data
    assert "user" not in serializer_data
    assert "user_id" not in serializer_data
    assert "paperless_url" in serializer_data
    assert serializer_data["paperless_url"] == profile.paperless_url
    assert "paperless_api_key" not in serializer_data
    assert "paperless_tika_enabled" in serializer_data
    assert serializer_data["paperless_tika_enabled"] == profile.paperless_tika_enabled
    assert "immich_url" in serializer_data
    assert serializer_data["immich_url"] == profile.immich_url
    assert "immich_api_key" not in serializer_data
    assert "nextcloud_url" in serializer_data
    assert serializer_data["nextcloud_url"] == profile.nextcloud_url
    assert "nextcloud_username" in serializer_data
    assert serializer_data["nextcloud_username"] == profile.nextcloud_username
    assert "nextcloud_password" not in serializer_data
    assert "nextcloud_addressbook" in serializer_data
    assert serializer_data["nextcloud_addressbook"] == profile.nextcloud_addressbook
    assert len(serializer_data) == 6


@pytest.mark.django_db
def test_input(profile_payload, request_context):
    """Tests for the expected input of the serializer."""
    assert "user" not in profile_payload

    serializer = UserProfileSerializer(data=profile_payload, context=request_context)
    assert serializer.is_valid()
    serializer_data = serializer.validated_data

    assert "id" not in serializer_data
    assert "user_id" not in serializer_data
    assert "paperless_url" in serializer_data
    assert serializer_data["paperless_url"] == profile_payload["paperless_url"]
    assert "paperless_api_key" in serializer_data
    assert serializer_data["paperless_api_key"] == profile_payload["paperless_api_key"]
    assert "paperless_tika_enabled" in serializer_data
    assert (
        serializer_data["paperless_tika_enabled"]
        == profile_payload["paperless_tika_enabled"]
    )
    assert "immich_url" in serializer_data
    assert serializer_data["immich_url"] == profile_payload["immich_url"]
    assert "immich_api_key" in serializer_data
    assert serializer_data["immich_api_key"] == profile_payload["immich_api_key"]
    assert "nextcloud_url" in serializer_data
    assert serializer_data["nextcloud_url"] == profile_payload["nextcloud_url"]
    assert (
        serializer_data["nextcloud_username"] == profile_payload["nextcloud_username"]
    )
    assert "nextcloud_password" in serializer_data
    assert (
        serializer_data["nextcloud_password"] == profile_payload["nextcloud_password"]
    )
    assert "nextcloud_addressbook" in serializer_data
    assert (
        serializer_data["nextcloud_addressbook"]
        == profile_payload["nextcloud_addressbook"]
    )
    assert "user" in serializer_data
    assert serializer_data["user"] == request_context["request"].user
    assert len(serializer_data) == 10
