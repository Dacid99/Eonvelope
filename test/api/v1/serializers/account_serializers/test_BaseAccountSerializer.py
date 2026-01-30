# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
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
from core.models import Account
from core.utils.fetchers.exceptions import MailAccountError


@pytest.fixture(autouse=True)
def auto_mock_Account_test(mock_Account_test):
    """All tests mock Accounts test."""


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
    assert "allow_insecure_connection" in serializer_data
    assert (
        serializer_data["allow_insecure_connection"]
        == fake_account.allow_insecure_connection
    )
    assert "is_healthy" in serializer_data
    assert serializer_data["is_healthy"] == fake_account.is_healthy
    assert "last_error" in serializer_data
    assert serializer_data["last_error"] == fake_account.last_error
    assert "last_error_occurred_at" in serializer_data
    assert (
        serializer_data["last_error_occurred_at"] == fake_account.last_error_occurred_at
    )
    assert "is_favorite" in serializer_data
    assert serializer_data["is_favorite"] == fake_account.is_favorite
    assert "created" in serializer_data
    assert datetime.fromisoformat(serializer_data["created"]) == fake_account.created
    assert "updated" in serializer_data
    assert datetime.fromisoformat(serializer_data["updated"]) == fake_account.updated
    assert "user" not in serializer_data
    assert len(serializer_data) == 12


@pytest.mark.django_db
def test_input__test_success(account_payload, request_context, mock_Account_test):
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
    assert "allow_insecure_connection" in serializer_data
    assert (
        serializer_data["allow_insecure_connection"]
        == account_payload["allow_insecure_connection"]
    )
    assert "is_healthy" not in serializer_data
    assert "last_error" not in serializer_data
    assert "last_error_occurred_at" not in serializer_data
    assert "is_favorite" in serializer_data
    assert serializer_data["is_favorite"] == account_payload["is_favorite"]
    assert "created" not in serializer_data
    assert "updated" not in serializer_data
    assert "user" in serializer_data
    assert serializer_data["user"] == request_context["request"].user
    assert len(serializer_data) == 8
    mock_Account_test.assert_called_once()


@pytest.mark.django_db
def test_input__test_failure(
    account_payload, request_context, mock_Account_test, fake_error_message
):
    """Tests for the expected input of the serializer."""
    mock_Account_test.side_effect = MailAccountError(ValueError(fake_error_message))

    serializer = BaseAccountSerializer(data=account_payload, context=request_context)
    assert not serializer.is_valid()
    assert len(serializer.errors) == 1
    assert "__all__" in serializer.errors
    assert len(serializer.errors["__all__"]) == 1
    assert fake_error_message in serializer.errors["__all__"][0]
    mock_Account_test.assert_called_once()


@pytest.mark.django_db
def test_input__no_test(fake_account, request_context, mock_Account_test):
    """Tests post direction of :class:`web.forms.BaseAccountForm`."""
    unchanged_data = model_to_dict(fake_account)
    unchanged_data.pop("user")
    unchanged_data.pop("id")

    serializer = BaseAccountSerializer(
        instance=fake_account, data=unchanged_data, context=request_context
    )

    assert serializer.is_valid()
    mock_Account_test.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("bad_mail_host_port", [-10, 98765])
def test_input__bad_mail_host_port(
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
def test_input__bad_protocol(
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
def test_input__bad_timeout(
    fake_account, account_payload, request_context, bad_timeout
):
    """Tests input direction of :class:`api.v1.serializers.BaseAccountSerializer`."""
    account_payload["timeout"] = bad_timeout

    serializer = BaseAccountSerializer(
        instance=fake_account, data=account_payload, context=request_context
    )

    assert not serializer.is_valid()
    assert serializer["timeout"].errors


@pytest.mark.django_db
def test_input__duplicate(fake_account, request_context):
    """Tests input direction of :class:`api.v1.serializers.BaseAccountSerializer`."""
    payload = model_to_dict(fake_account)
    payload.pop("id")
    payload.pop("user")
    clean_payload = {key: value for key, value in payload.items() if value is not None}

    serializer = BaseAccountSerializer(data=clean_payload, context=request_context)

    assert not serializer.is_valid()
    assert serializer.errors


@pytest.mark.django_db
def test_save(account_payload, request_context, mock_Account_update_mailboxes):
    """Tests saving of :class:`api.v1.serializers.BaseAccountSerializer`."""
    form = BaseAccountSerializer(data=account_payload, context=request_context)

    assert Account.objects.count() == 1

    assert form.is_valid()
    form.save()

    assert Account.objects.count() == 2
    mock_Account_update_mailboxes.assert_called_once()
