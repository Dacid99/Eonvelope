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

"""Test module for :mod:`api.v1.serializers.CorrespondentSerializers.BaseCorrespondentSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.correspondent_serializers.BaseCorrespondentSerializer import (
    BaseCorrespondentSerializer,
)


@pytest.mark.django_db
def test_output(correspondentModel, emailModel):
    """Tests for the expected output of the serializer."""
    serializerData = BaseCorrespondentSerializer(instance=correspondentModel).data

    assert "id" in serializerData
    assert serializerData["id"] == correspondentModel.id
    assert "emails" not in serializerData
    assert "mailinglist" not in serializerData
    assert "email_name" in serializerData
    assert serializerData["email_name"] == correspondentModel.email_name
    assert "email_address" in serializerData
    assert serializerData["email_address"] == correspondentModel.email_address
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == correspondentModel.is_favorite
    assert "created" in serializerData
    assert (
        datetime.fromisoformat(serializerData["created"]) == correspondentModel.created
    )
    assert "updated" in serializerData
    assert (
        datetime.fromisoformat(serializerData["updated"]) == correspondentModel.updated
    )
    assert len(serializerData) == 6


@pytest.mark.django_db
def test_input(correspondentModel, emailModel):
    """Tests for the expected input of the serializer."""
    serializer = BaseCorrespondentSerializer(data=model_to_dict(correspondentModel))
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert "id" not in serializerData
    assert "emails" not in serializerData
    assert "mailinglist" not in serializerData
    assert "email_name" in serializerData
    assert serializerData["email_name"] == correspondentModel.email_name
    assert "email_address" not in serializerData
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == correspondentModel.is_favorite
    assert "created" not in serializerData
    assert "updated" not in serializerData
    assert len(serializerData) == 2
