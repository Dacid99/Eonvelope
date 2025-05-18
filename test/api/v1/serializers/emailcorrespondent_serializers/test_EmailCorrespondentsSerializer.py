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

"""Test module for :mod:`api.v1.serializers.EmailCorrespondentSerializer`."""

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.emailcorrespondent_serializers.EmailCorrespondentSerializer import (
    EmailCorrespondentSerializer,
)


@pytest.mark.django_db
def test_output(fake_emailcorrespondent, request_context):
    """Tests for the expected output of the serializer."""
    serializer_data = EmailCorrespondentSerializer(
        instance=fake_emailcorrespondent, context=request_context
    ).data

    assert "id" not in serializer_data
    assert "email" not in serializer_data
    assert "correspondent" in serializer_data
    assert isinstance(serializer_data["correspondent"], dict)
    assert "mention" in serializer_data
    assert serializer_data["mention"] == fake_emailcorrespondent.mention
    assert "created" not in serializer_data
    assert "updated" not in serializer_data
    assert len(serializer_data) == 2


@pytest.mark.django_db
def test_input(fake_emailcorrespondent, request_context):
    """Tests for the expected input of the serializer."""
    serializer = EmailCorrespondentSerializer(
        data=model_to_dict(fake_emailcorrespondent), context=request_context
    )
    assert serializer.is_valid()
    serializer_data = serializer.validated_data

    assert "id" not in serializer_data
    assert "email" not in serializer_data
    assert "correspondent" not in serializer_data
    assert "mention" not in serializer_data
    assert "created" not in serializer_data
    assert "updated" not in serializer_data
    assert len(serializer_data) == 0
