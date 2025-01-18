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

"""Test module for :mod:`Emailkasten.Serializers.AttachmentSerializers.BaseAttachmentSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from Emailkasten.Serializers.AttachmentSerializers.BaseAttachmentSerializer import BaseAttachmentSerializer

from ...models.test_AttachmentModel import fixture_attachmentModel


@pytest.mark.django_db
def test_output(attachment):
    """Tests for the expected output of the serializer."""
    serializerData = BaseAttachmentSerializer(instance=attachment).data

    assert 'id' in serializerData
    assert serializerData['id'] == attachment.id
    assert 'file_path' not in serializerData
    assert 'file_name' in serializerData
    assert serializerData['file_name'] == attachment.file_name
    assert 'datasize' in serializerData
    assert serializerData['datasize'] == attachment.datasize
    assert 'is_favorite' in serializerData
    assert serializerData['is_favorite'] == attachment.is_favorite
    assert 'email' in serializerData
    assert serializerData['email'] == attachment.email.id
    assert 'created' in serializerData
    assert datetime.fromisoformat(serializerData['created']) == attachment.created
    assert 'updated' in serializerData
    assert datetime.fromisoformat(serializerData['updated']) == attachment.updated
    assert len(serializerData) == 7


@pytest.mark.django_db
def test_input(attachment):
    """Tests for the expected input of the serializer."""
    serializer = BaseAttachmentSerializer(data=model_to_dict(attachment))
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert 'id' not in serializerData
    assert 'file_path' not in serializerData
    assert 'file_name' not in serializerData
    assert 'datasize' not in serializerData
    assert 'is_favorite' in serializerData
    assert serializerData['is_favorite'] == attachment.is_favorite
    assert 'email' not in serializerData
    assert 'created' not in serializerData
    assert 'updated' not in serializerData
    assert len(serializerData) == 1
