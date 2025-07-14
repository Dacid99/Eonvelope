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

"""Test module for :mod:`api.v1.serializers.CorrespondentSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.correspondent_serializers.CorrespondentSerializer import (
    CorrespondentSerializer,
)


@pytest.mark.django_db
def test_output(fake_correspondent, request_context):
    """Tests for the expected output of the serializer."""
    serializer_data = CorrespondentSerializer(
        instance=fake_correspondent, context=request_context
    ).data

    assert "id" in serializer_data
    assert serializer_data["id"] == fake_correspondent.id
    assert "emails" in serializer_data
    assert isinstance(serializer_data["emails"], list)
    assert len(serializer_data["emails"]) == 1
    assert isinstance(serializer_data["emails"][0], dict)
    assert "email_name" in serializer_data
    assert serializer_data["email_name"] == fake_correspondent.email_name
    assert "email_address" in serializer_data
    assert serializer_data["email_address"] == fake_correspondent.email_address
    assert "list_id" in serializer_data
    assert serializer_data["list_id"] == fake_correspondent.list_id
    assert "list_owner" in serializer_data
    assert serializer_data["list_owner"] == fake_correspondent.list_owner
    assert "list_subscribe" in serializer_data
    assert serializer_data["list_subscribe"] == fake_correspondent.list_subscribe
    assert "list_unsubscribe" in serializer_data
    assert serializer_data["list_unsubscribe"] == fake_correspondent.list_unsubscribe
    assert "list_unsubscribe_post" in serializer_data
    assert (
        serializer_data["list_unsubscribe"] == fake_correspondent.list_unsubscribe_post
    )
    assert "list_post" in serializer_data
    assert serializer_data["list_post"] == fake_correspondent.list_post
    assert "list_help" in serializer_data
    assert serializer_data["list_help"] == fake_correspondent.list_help
    assert "list_archive" in serializer_data
    assert serializer_data["list_archive"] == fake_correspondent.list_archive
    assert "is_favorite" in serializer_data
    assert serializer_data["is_favorite"] == fake_correspondent.is_favorite
    assert "created" in serializer_data
    assert (
        datetime.fromisoformat(serializer_data["created"]) == fake_correspondent.created
    )
    assert "updated" in serializer_data
    assert (
        datetime.fromisoformat(serializer_data["updated"]) == fake_correspondent.updated
    )
    assert len(serializer_data) == 15


@pytest.mark.django_db
def test_input(fake_correspondent, request_context):
    """Tests for the expected input of the serializer."""
    serializer = CorrespondentSerializer(
        data=model_to_dict(fake_correspondent), context=request_context
    )
    assert serializer.is_valid()
    serializer_data = serializer.validated_data

    assert "id" not in serializer_data
    assert "emails" not in serializer_data
    assert "email_name" in serializer_data
    assert serializer_data["email_name"] == fake_correspondent.email_name
    assert "email_address" not in serializer_data
    assert "list_id" not in serializer_data
    assert "list_owner" not in serializer_data
    assert "list_subscribe" not in serializer_data
    assert "list_unsubscribe" not in serializer_data
    assert "list_unsubscribe_post" not in serializer_data
    assert "list_post" not in serializer_data
    assert "list_help" not in serializer_data
    assert "list_archive" not in serializer_data
    assert "is_favorite" in serializer_data
    assert serializer_data["is_favorite"] == fake_correspondent.is_favorite
    assert "created" not in serializer_data
    assert "updated" not in serializer_data
    assert len(serializer_data) == 2
