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

"""Test module for :mod:`api.v1.serializers.EmailCorrespondentSerializers.BaseEmailCorrespondentSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.emailcorrespondent_serializers.BaseEmailCorrespondentSerializer import (
    BaseEmailCorrespondentSerializer,
)


@pytest.mark.django_db
def test_output(fake_emailCorrespondent, request_context):
    """Tests for the expected output of the serializer."""
    serializerData = BaseEmailCorrespondentSerializer(
        instance=fake_emailCorrespondent, context=request_context
    ).data

    assert "id" in serializerData
    assert serializerData["id"] == fake_emailCorrespondent.id
    assert "email" in serializerData
    assert serializerData["email"] == fake_emailCorrespondent.email.id
    assert "correspondent" in serializerData
    assert serializerData["correspondent"] == fake_emailCorrespondent.correspondent.id
    assert "mention" in serializerData
    assert serializerData["mention"] == fake_emailCorrespondent.mention
    assert "created" in serializerData
    assert (
        datetime.fromisoformat(serializerData["created"])
        == fake_emailCorrespondent.created
    )
    assert "updated" in serializerData
    assert (
        datetime.fromisoformat(serializerData["updated"])
        == fake_emailCorrespondent.updated
    )
    assert len(serializerData) == 6


@pytest.mark.django_db
def test_input(fake_emailCorrespondent, request_context):
    """Tests for the expected input of the serializer."""
    serializer = BaseEmailCorrespondentSerializer(
        data=model_to_dict(fake_emailCorrespondent), context=request_context
    )
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert "id" not in serializerData
    assert "email" not in serializerData
    assert "correspondent" not in serializerData
    assert "mention" not in serializerData
    assert "created" not in serializerData
    assert "updated" not in serializerData
    assert len(serializerData) == 0
