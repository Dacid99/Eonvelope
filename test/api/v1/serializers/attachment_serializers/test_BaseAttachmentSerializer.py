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

"""Test module for :mod:`api.v1.serializers.AttachmentSerializers.BaseAttachmentSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.attachment_serializers.BaseAttachmentSerializer import (
    BaseAttachmentSerializer,
)


@pytest.mark.django_db
def test_output(fake_attachment, request_context):
    """Tests for the expected output of the serializer."""
    serializerData = BaseAttachmentSerializer(
        instance=fake_attachment, context=request_context
    ).data

    assert "id" in serializerData
    assert serializerData["id"] == fake_attachment.id
    assert "file_path" not in serializerData
    assert "file_name" in serializerData
    assert serializerData["file_name"] == fake_attachment.file_name
    assert "content_disposition" in serializerData
    assert serializerData["content_disposition"] == fake_attachment.content_disposition
    assert "content_id" in serializerData
    assert serializerData["content_id"] == fake_attachment.content_id
    assert "content_maintype" in serializerData
    assert serializerData["content_maintype"] == fake_attachment.content_maintype
    assert "content_subtype" in serializerData
    assert serializerData["content_subtype"] == fake_attachment.content_subtype
    assert "datasize" in serializerData
    assert serializerData["datasize"] == fake_attachment.datasize
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == fake_attachment.is_favorite
    assert "email" in serializerData
    assert serializerData["email"] == fake_attachment.email.id
    assert "created" in serializerData
    assert datetime.fromisoformat(serializerData["created"]) == fake_attachment.created
    assert "updated" in serializerData
    assert datetime.fromisoformat(serializerData["updated"]) == fake_attachment.updated
    assert len(serializerData) == 11


@pytest.mark.django_db
def test_input(fake_attachment, request_context):
    """Tests for the expected input of the serializer."""
    serializer = BaseAttachmentSerializer(
        data=model_to_dict(fake_attachment), context=request_context
    )
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert "id" not in serializerData
    assert "file_path" not in serializerData
    assert "file_name" not in serializerData
    assert "content_disposition" not in serializerData
    assert "content_id" not in serializerData
    assert "content_maintype" not in serializerData
    assert "content_subtype" not in serializerData
    assert "datasize" not in serializerData
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == fake_attachment.is_favorite
    assert "email" not in serializerData
    assert "created" not in serializerData
    assert "updated" not in serializerData
    assert len(serializerData) == 1
