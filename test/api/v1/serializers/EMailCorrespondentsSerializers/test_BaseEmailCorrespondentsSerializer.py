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

"""Test module for :mod:`api.v1.serializers.EMailCorrespondentsSerializers.BaseEMailCorrespondentSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.emailcorrespondents_serializers.BaseEMailCorrespondentSerializer import (
    BaseEMailCorrespondentSerializer,
)


@pytest.mark.django_db
def test_output(emailModel):
    """Tests for the expected output of the serializer."""
    emailCorrespondentModel = emailModel.emailcorrespondents.first()

    serializerData = BaseEMailCorrespondentSerializer(
        instance=emailCorrespondentModel
    ).data

    assert "id" in serializerData
    assert serializerData["id"] == emailCorrespondentModel.id
    assert "email" in serializerData
    assert serializerData["email"] == emailCorrespondentModel.email.id
    assert "correspondent" in serializerData
    assert serializerData["correspondent"] == emailCorrespondentModel.correspondent.id
    assert "mention" in serializerData
    assert serializerData["mention"] == emailCorrespondentModel.mention
    assert "created" in serializerData
    assert (
        datetime.fromisoformat(serializerData["created"])
        == emailCorrespondentModel.created
    )
    assert "updated" in serializerData
    assert (
        datetime.fromisoformat(serializerData["updated"])
        == emailCorrespondentModel.updated
    )
    assert len(serializerData) == 6


@pytest.mark.django_db
def test_input(emailModel):
    """Tests for the expected input of the serializer."""
    emailCorrespondentModel = emailModel.emailcorrespondents.first()

    serializer = BaseEMailCorrespondentSerializer(
        data=model_to_dict(emailCorrespondentModel)
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
