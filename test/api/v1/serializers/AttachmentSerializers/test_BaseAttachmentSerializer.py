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
def test_output(attachmentModel, request_context):
    """Tests for the expected output of the serializer."""
    serializerData = BaseAttachmentSerializer(
        instance=attachmentModel, context=request_context
    ).data

    assert "id" in serializerData
    assert serializerData["id"] == attachmentModel.id
    assert "file_path" not in serializerData
    assert "file_name" in serializerData
    assert serializerData["file_name"] == attachmentModel.file_name
    assert "content_disposition" in serializerData
    assert serializerData["content_disposition"] == attachmentModel.content_disposition
    assert "content_type" in serializerData
    assert serializerData["content_type"] == attachmentModel.content_type
    assert "datasize" in serializerData
    assert serializerData["datasize"] == attachmentModel.datasize
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == attachmentModel.is_favorite
    assert "email" in serializerData
    assert serializerData["email"] == attachmentModel.email.id
    assert "created" in serializerData
    assert datetime.fromisoformat(serializerData["created"]) == attachmentModel.created
    assert "updated" in serializerData
    assert datetime.fromisoformat(serializerData["updated"]) == attachmentModel.updated
    assert len(serializerData) == 9


@pytest.mark.django_db
def test_input(attachmentModel, request_context):
    """Tests for the expected input of the serializer."""
    serializer = BaseAttachmentSerializer(
        data=model_to_dict(attachmentModel), context=request_context
    )
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert "id" not in serializerData
    assert "file_path" not in serializerData
    assert "file_name" not in serializerData
    assert "content_disposition" not in serializerData
    assert "content_type" not in serializerData
    assert "datasize" not in serializerData
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == attachmentModel.is_favorite
    assert "email" not in serializerData
    assert "created" not in serializerData
    assert "updated" not in serializerData
    assert len(serializerData) == 1
