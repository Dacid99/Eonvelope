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

"""Test module for :mod:`api.v1.serializers.BaseAttachmentSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.attachment_serializers.BaseAttachmentSerializer import (
    BaseAttachmentSerializer,
)


@pytest.mark.django_db
def test_output(fake_attachment, request_context):
    """Tests for the expected output of the serializer."""
    serializer_data = BaseAttachmentSerializer(
        instance=fake_attachment, context=request_context
    ).data

    assert "id" in serializer_data
    assert serializer_data["id"] == fake_attachment.id
    assert "file_path" not in serializer_data
    assert "file_name" in serializer_data
    assert serializer_data["file_name"] == fake_attachment.file_name
    assert "content_disposition" in serializer_data
    assert serializer_data["content_disposition"] == fake_attachment.content_disposition
    assert "content_id" in serializer_data
    assert serializer_data["content_id"] == fake_attachment.content_id
    assert "content_maintype" in serializer_data
    assert serializer_data["content_maintype"] == fake_attachment.content_maintype
    assert "content_subtype" in serializer_data
    assert serializer_data["content_subtype"] == fake_attachment.content_subtype
    assert "datasize" in serializer_data
    assert serializer_data["datasize"] == fake_attachment.datasize
    assert "is_favorite" in serializer_data
    assert serializer_data["is_favorite"] == fake_attachment.is_favorite
    assert "email" in serializer_data
    assert serializer_data["email"] == fake_attachment.email.id
    assert "created" in serializer_data
    assert datetime.fromisoformat(serializer_data["created"]) == fake_attachment.created
    assert "updated" in serializer_data
    assert datetime.fromisoformat(serializer_data["updated"]) == fake_attachment.updated
    assert len(serializer_data) == 11


@pytest.mark.django_db
def test_input(fake_attachment, request_context):
    """Tests for the expected input of the serializer."""
    serializer = BaseAttachmentSerializer(
        data=model_to_dict(fake_attachment), context=request_context
    )
    assert serializer.is_valid()
    serializer_data = serializer.validated_data

    assert "id" not in serializer_data
    assert "file_path" not in serializer_data
    assert "file_name" not in serializer_data
    assert "content_disposition" not in serializer_data
    assert "content_id" not in serializer_data
    assert "content_maintype" not in serializer_data
    assert "content_subtype" not in serializer_data
    assert "datasize" not in serializer_data
    assert "is_favorite" in serializer_data
    assert serializer_data["is_favorite"] == fake_attachment.is_favorite
    assert "email" not in serializer_data
    assert "created" not in serializer_data
    assert "updated" not in serializer_data
    assert len(serializer_data) == 1
