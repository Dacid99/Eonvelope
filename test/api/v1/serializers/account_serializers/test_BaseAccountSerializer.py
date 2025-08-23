# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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

"""Test module for :mod:`api.v1.serializers.BaseAccountSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.account_serializers.BaseAccountSerializer import (
    BaseAccountSerializer,
)


@pytest.mark.django_db
def test_output(fake_account, request_context):
    """Tests for the expected output of the serializer."""
    serializer_data = BaseAccountSerializer(
        instance=fake_account, context=request_context
    ).data

    assert "id" in serializer_data
    assert serializer_data["id"] == fake_account.id
    assert "password" not in serializer_data
    assert "mail_address" in serializer_data
    assert serializer_data["mail_address"] == fake_account.mail_address
    assert "mail_host" in serializer_data
    assert serializer_data["mail_host"] == fake_account.mail_host
    assert "mail_host_port" in serializer_data
    assert serializer_data["mail_host_port"] == fake_account.mail_host_port
    assert "protocol" in serializer_data
    assert serializer_data["protocol"] == fake_account.protocol
    assert "timeout" in serializer_data
    assert serializer_data["timeout"] == fake_account.timeout
    assert "is_healthy" in serializer_data
    assert serializer_data["is_healthy"] == fake_account.is_healthy
    assert "is_favorite" in serializer_data
    assert serializer_data["is_favorite"] == fake_account.is_favorite
    assert "created" in serializer_data
    assert datetime.fromisoformat(serializer_data["created"]) == fake_account.created
    assert "updated" in serializer_data
    assert datetime.fromisoformat(serializer_data["updated"]) == fake_account.updated

    assert "user" not in serializer_data
    assert len(serializer_data) == 10


@pytest.mark.django_db
def test_input(account_payload, request_context):
    """Tests for the expected input of the serializer."""
    assert "user" not in account_payload

    serializer = BaseAccountSerializer(data=account_payload, context=request_context)
    assert serializer.is_valid()
    serializer_data = serializer.validated_data

    assert "id" not in serializer_data
    assert "password" in serializer_data
    assert serializer_data["password"] == account_payload["password"]
    assert "mail_address" in serializer_data
    assert serializer_data["mail_address"] == account_payload["mail_address"]
    assert "mail_host" in serializer_data
    assert serializer_data["mail_host"] == account_payload["mail_host"]
    assert "mail_host_port" in serializer_data
    assert serializer_data["mail_host_port"] == account_payload["mail_host_port"]
    assert "protocol" in serializer_data
    assert serializer_data["protocol"] == account_payload["protocol"]
    assert "timeout" in serializer_data
    assert serializer_data["timeout"] == account_payload["timeout"]
    assert "is_healthy" not in serializer_data
    assert "is_favorite" in serializer_data
    assert serializer_data["is_favorite"] == account_payload["is_favorite"]
    assert "created" not in serializer_data
    assert "updated" not in serializer_data
    assert "user" in serializer_data
    assert serializer_data["user"] == request_context["request"].user
    assert len(serializer_data) == 8


@pytest.mark.django_db
@pytest.mark.parametrize("bad_mail_address", ["nomail", "email@email@multi@.com"])
def test_input_bad_mail_address(
    fake_account, account_payload, request_context, bad_mail_address
):
    """Tests input direction of :class:`api.v1.serializers.BaseAccountSerializer`."""
    account_payload["mail_address"] = bad_mail_address

    serializer = BaseAccountSerializer(
        instance=fake_account, data=account_payload, context=request_context
    )

    assert not serializer.is_valid()
    assert serializer["mail_address"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_mail_host_port", [-10, 98765])
def test_input_bad_mail_host_port(
    fake_account, account_payload, request_context, bad_mail_host_port
):
    """Tests input direction of :class:`api.v1.serializers.BaseAccountSerializer`."""
    account_payload["mail_host_port"] = bad_mail_host_port

    serializer = BaseAccountSerializer(
        instance=fake_account, data=account_payload, context=request_context
    )

    assert not serializer.is_valid()
    assert serializer["mail_host_port"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_protocol", ["other"])
def test_input_bad_protocol(
    fake_account, account_payload, request_context, bad_protocol
):
    """Tests input direction of :class:`api.v1.serializers.BaseAccountSerializer`."""
    account_payload["protocol"] = bad_protocol

    serializer = BaseAccountSerializer(
        instance=fake_account, data=account_payload, context=request_context
    )

    assert not serializer.is_valid()
    assert serializer["protocol"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_timeout", [-1])
def test_input_bad_timeout(fake_account, account_payload, request_context, bad_timeout):
    """Tests input direction of :class:`api.v1.serializers.BaseAccountSerializer`."""
    account_payload["timeout"] = bad_timeout

    serializer = BaseAccountSerializer(
        instance=fake_account, data=account_payload, context=request_context
    )

    assert not serializer.is_valid()
    assert serializer["timeout"].errors


@pytest.mark.django_db
def test_input_duplicate(fake_account, request_context):
    """Tests input direction of :class:`api.v1.serializers.BaseAccountSerializer`."""
    payload = model_to_dict(fake_account)
    payload.pop("id")
    payload.pop("user")
    clean_payload = {key: value for key, value in payload.items() if value is not None}

    serializer = BaseAccountSerializer(data=clean_payload, context=request_context)

    assert not serializer.is_valid()
    assert serializer.errors
