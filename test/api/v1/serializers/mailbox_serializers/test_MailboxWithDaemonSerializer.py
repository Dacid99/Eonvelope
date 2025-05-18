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

"""Test module for :mod:`api.v1.serializers.MailboxWithDaemonSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.mailbox_serializers.MailboxWithDaemonSerializer import (
    MailboxWithDaemonSerializer,
)


@pytest.mark.django_db
def test_output(fake_mailbox, request_context):
    """Tests for the expected output of the serializer."""
    serializer_data = MailboxWithDaemonSerializer(
        instance=fake_mailbox, context=request_context
    ).data

    assert "id" in serializer_data
    assert serializer_data["id"] == fake_mailbox.id
    assert "daemons" in serializer_data
    assert isinstance(serializer_data["daemons"], list)
    assert len(serializer_data["daemons"]) == 1
    assert isinstance(serializer_data["daemons"][0], dict)
    assert "name" in serializer_data
    assert serializer_data["name"] == fake_mailbox.name
    assert "account" in serializer_data
    assert serializer_data["account"] == fake_mailbox.account.id
    assert "save_attachments" in serializer_data
    assert serializer_data["save_attachments"] == fake_mailbox.save_attachments
    assert "save_to_eml" in serializer_data
    assert serializer_data["save_to_eml"] == fake_mailbox.save_to_eml
    assert "save_to_html" in serializer_data
    assert serializer_data["save_to_html"] == fake_mailbox.save_to_html
    assert "is_favorite" in serializer_data
    assert serializer_data["is_favorite"] == fake_mailbox.is_favorite
    assert "is_healthy" in serializer_data
    assert serializer_data["is_healthy"] == fake_mailbox.is_healthy
    assert "created" in serializer_data
    assert datetime.fromisoformat(serializer_data["created"]) == fake_mailbox.created
    assert "updated" in serializer_data
    assert datetime.fromisoformat(serializer_data["updated"]) == fake_mailbox.updated
    assert len(serializer_data) == 11


@pytest.mark.django_db
def test_input(fake_mailbox, request_context):
    """Tests for the expected input of the serializer."""
    serializer = MailboxWithDaemonSerializer(
        data=model_to_dict(fake_mailbox), context=request_context
    )
    assert serializer.is_valid()
    serializer_data = serializer.validated_data

    assert "id" not in serializer_data
    assert "daemons" not in serializer_data
    assert "name" not in serializer_data
    assert "account" not in serializer_data
    assert "save_attachments" in serializer_data
    assert serializer_data["save_attachments"] == fake_mailbox.save_attachments
    assert "save_to_eml" in serializer_data
    assert serializer_data["save_to_eml"] == fake_mailbox.save_to_eml
    assert "save_to_html" in serializer_data
    assert serializer_data["save_to_html"] == fake_mailbox.save_to_html
    assert "is_favorite" in serializer_data
    assert serializer_data["is_favorite"] == fake_mailbox.is_favorite
    assert "is_healthy" not in serializer_data
    assert "created" not in serializer_data
    assert "updated" not in serializer_data
    assert len(serializer_data) == 4
