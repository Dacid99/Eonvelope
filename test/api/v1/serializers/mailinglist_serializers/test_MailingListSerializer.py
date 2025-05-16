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

"""Test module for :mod:`api.v1.serializers.MailingListSerializers.MailingListSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.mailinglist_serializers.MailingListSerializer import (
    MailingListSerializer,
)


@pytest.mark.django_db
def test_output(fake_mailingList, request_context):
    """Tests for the expected output of the serializer."""
    serializerData = MailingListSerializer(
        instance=fake_mailingList, context=request_context
    ).data

    assert "id" in serializerData
    assert serializerData["id"] == fake_mailingList.id
    assert "list_id" in serializerData
    assert serializerData["list_id"] == fake_mailingList.list_id
    assert "list_owner" in serializerData
    assert serializerData["list_owner"] == fake_mailingList.list_owner
    assert "list_subscribe" in serializerData
    assert serializerData["list_subscribe"] == fake_mailingList.list_subscribe
    assert "list_unsubscribe" in serializerData
    assert serializerData["list_unsubscribe"] == fake_mailingList.list_unsubscribe
    assert "list_post" in serializerData
    assert serializerData["list_post"] == fake_mailingList.list_post
    assert "list_help" in serializerData
    assert serializerData["list_help"] == fake_mailingList.list_help
    assert "list_archive" in serializerData
    assert serializerData["list_archive"] == fake_mailingList.list_archive
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == fake_mailingList.is_favorite
    assert "from_correspondents" in serializerData
    assert isinstance(serializerData["from_correspondents"], list)
    assert len(serializerData["from_correspondents"]) == 1
    assert isinstance(serializerData["from_correspondents"][0], dict)
    assert "created" in serializerData
    assert datetime.fromisoformat(serializerData["created"]) == fake_mailingList.created
    assert "updated" in serializerData
    assert datetime.fromisoformat(serializerData["updated"]) == fake_mailingList.updated
    assert "emails" in serializerData
    assert isinstance(serializerData["emails"], list)
    assert len(serializerData["emails"]) == 1
    assert isinstance(serializerData["emails"][0], dict)
    assert len(serializerData) == 13


@pytest.mark.django_db
def test_input(fake_mailingList, request_context):
    """Tests for the expected input of the serializer."""
    serializer = MailingListSerializer(
        data=model_to_dict(fake_mailingList), context=request_context
    )
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert "id" not in serializerData
    assert "list_id" not in serializerData
    assert "list_owner" not in serializerData
    assert "list_subscribe" not in serializerData
    assert "list_unsubscribe" not in serializerData
    assert "list_post" not in serializerData
    assert "list_help" not in serializerData
    assert "list_archive" not in serializerData
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == fake_mailingList.is_favorite
    assert "from_correspondents" not in serializerData
    assert "created" not in serializerData
    assert "updated" not in serializerData
    assert "emails" not in serializerData
    assert len(serializerData) == 1
